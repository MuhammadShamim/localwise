"""
🧠 LocalWise v1.0.0 - Document Processing Engine (Modular)

Developed by: Akhtar Shamim (WWEX Group)
Version: 1.0.0  
License: MIT

Streamlined main entry point using modular components.
"""

import sys
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Import LocalWise modules
from localwise import config
from localwise.cli.cli_interface import handle_command_line_args, handle_clean_start, handle_status, handle_list_files, launch_streamlit_app
from localwise.core.file_processors import FileProcessorRegistry
from localwise.data.change_detector import detect_file_changes
from localwise.data.file_manifest import load_file_manifest
from localwise.data.data_manager import save_processed_data, load_processed_data
from localwise.core.embedding_service import create_embeddings_from_processed_data, create_embeddings_from_texts


def process_documents(folder, logger, incremental_mode=False, force_refresh=False):
    """Process documents using the modular system."""
    registry = FileProcessorRegistry()
    
    if incremental_mode:
        # Incremental processing mode
        logger.info("Starting incremental document processing...")
        print("🔄 Incremental Document Processing")
        print("   Detecting file changes...")
        
        change_info = detect_file_changes(folder, logger, force_refresh)
        files_to_process = change_info["to_process"]
        
        if not files_to_process:
            logger.info("No new or modified files found")
            print("✅ No changes detected - all files up to date")
            print("💡 Use --force-refresh to reprocess all files")
            return []
        
        print(f"📋 Changes detected:")
        if change_info["new"]:
            print(f"   🆕 New files: {len(change_info['new'])}")
        if change_info["modified"]:
            print(f"   📝 Modified files: {len(change_info['modified'])}")
        if change_info["deleted"]:
            print(f"   🗑️ Deleted files: {len(change_info['deleted'])}")
        
        # Group files by type for processing
        files_by_type = {}
        manifest = load_file_manifest()
        for file_path in files_to_process:
            if file_path in manifest:
                file_type = manifest[file_path]["type"]
                if file_type not in files_by_type:
                    files_by_type[file_type] = []
                files_by_type[file_type].append(file_path)
        
        print(f"\\n🔄 Processing {len(files_to_process)} changed files...")
        return registry.process_files_by_type(files_by_type, logger, config.MAX_FILE_SIZE_MB)
    
    else:
        # Full processing mode
        logger.info(f"Loading files from '{folder}/'...")
        print(f"📖 Loading files from '{folder}/'...")
        print("   Supported formats: 30+ file types including PDF, DOC, TXT, source code, and more")
        print("   🔍 Scanning subdirectories recursively...")
        
        all_docs = registry.scan_folder(folder, logger)
        
        if all_docs:
            print(f"✅ Found {len(all_docs)} document pages/rows across multiple file types")
        
        return all_docs


def process_step1(logger, incremental_mode=False, force_refresh=False):
    """Step 1: Process documents and extract text."""
    # Validate directories first
    is_valid, dir_msg = config.validate_directories()
    if not is_valid:
        logger.error(f"Directory validation failed: {dir_msg}")
        print(f"❌ Error: {dir_msg}")
        return False
    
    if dir_msg:
        logger.info(dir_msg)
        print(f"✅ {dir_msg}")
        print("Add your documents there, then run this script again.")
        return False

    # Process documents
    all_docs = process_documents(config.DOCS_FOLDER, logger, incremental_mode, force_refresh)
    
    if not all_docs:
        logger.warning(f"No supported files found in '{config.DOCS_FOLDER}/'")
        print(f"⚠️  No supported files found in '{config.DOCS_FOLDER}/'.")
        print("   Add your files and try again.")
        return False

    logger.info(f"Loaded {len(all_docs)} document pages/rows")
    print(f"✅ Loaded {len(all_docs)} document pages/rows")

    # Split into chunks
    logger.info("Splitting text into chunks...")
    print("🔄 Splitting text into chunks...")
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP
    )
    texts = []
    metadatas = []
    
    for doc in all_docs:
        try:
            chunks = splitter.split_text(doc["text"])
            texts.extend(chunks)
            metadatas.extend([{"source": doc["source"]}] * len(chunks))
        except Exception as e:
            logger.error(f"Error processing document {doc['source']}: {e}")
            continue

    if not texts:
        logger.error("No text chunks created")
        print("❌ Error: No text chunks could be created from your documents")
        return False
        
    logger.info(f"Created {len(texts)} chunks total")
    print(f"✅ Created {len(texts)} chunks total")
    
    # Save processed data
    save_processed_data(texts, metadatas, logger, incremental_mode)
    return True


def main():
    """Main entry point."""
    # Setup logging
    logger = config.setup_logging()
    logger.info("Starting LocalWise document processing...")

    try:
        # Handle command line arguments
        args = handle_command_line_args()
        if args is None:
            return

        # Handle special commands first
        if args.clean_start:
            handle_clean_start(logger)
            return
        
        if args.status:
            handle_status()
            return
        
        if args.list_files:
            handle_list_files()
            return

        # Handle main processing steps
        if args.step1:
            success = process_step1(logger, args.incremental, args.force_refresh)
            if not success:
                sys.exit(1)
                
        elif args.step2:
            success = create_embeddings_from_processed_data(logger)
            if not success:
                sys.exit(1)
                
        elif args.step3:
            success = launch_streamlit_app(logger)
            if not success:
                sys.exit(1)
                
        elif args.incremental:
            success = process_step1(logger, incremental_mode=True)
            if not success:
                sys.exit(1)
                
        else:
            # Default: Full processing (Steps 1 + 2)
            print("🚀 LocalWise Full Processing Pipeline")
            print("=" * 50)
            
            # Step 1: Process documents
            success = process_step1(logger)
            if not success:
                sys.exit(1)
            
            # Step 2: Create embeddings
            success = create_embeddings_from_processed_data(logger)
            if not success:
                sys.exit(1)
            
            print("\\n✅ Success! LocalWise is ready to use")
            print("🚀 Next step: streamlit run app.py")
                
    except KeyboardInterrupt:
        logger.info("Processing interrupted by user")
        print("\\n❌ Processing interrupted. Your progress has been saved.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()