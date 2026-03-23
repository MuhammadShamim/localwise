/* 
 * Sample Java file for LocalWise processing
 * Tests Java source code ingestion and processing
 */

package com.localwise.test;

import java.util.*;

/**
 * LocalWise Java Processing Test
 * 
 * This class demonstrates the Java file processing capabilities
 * added to LocalWise v1.0.0.
 * 
 * @author LocalWise Team
 * @version 1.0.0
 */
public class LocalWiseTest {
    
    private static final String VERSION = "1.0.0";
    private final List<String> supportedFormats;
    
    /**
     * Constructor for LocalWiseTest
     */
    public LocalWiseTest() {
        this.supportedFormats = Arrays.asList(
            "PDF", "CSV", "JSON", "YAML", "XML",
            "TXT", "RTF", "DOC", "DOCX",
            "Java", "Python", "SQL", "JavaScript", "TypeScript",
            "C", "C++", "C#", "Go", "PHP", "Ruby", "Rust",
            "HTML", "CSS", "Markdown"
        );
    }
    
    /**
     * Gets the list of supported file formats
     * @return List of supported formats
     */
    public List<String> getSupportedFormats() {
        return new ArrayList<>(supportedFormats);
    }
    
    /**
     * Processes a document with the given name
     * @param documentName The name of the document to process
     * @return Processing result message
     */
    public String processDocument(String documentName) {
        return String.format("Processing document: %s with LocalWise %s", 
                           documentName, VERSION);
    }
    
    /**
     * Main method for testing
     */
    public static void main(String[] args) {
        LocalWiseTest test = new LocalWiseTest();
        
        System.out.println("LocalWise Java Processing Test");
        System.out.println("==============================");
        
        // Display supported formats
        System.out.println("Supported formats:");
        test.getSupportedFormats().forEach(format -> 
            System.out.println("- " + format)
        );
        
        // Test document processing
        String result = test.processDocument("sample_java_file.java");
        System.out.println("\n" + result);
    }
}