package evmeval;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

import org.apache.commons.cli.BasicParser;
import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.HelpFormatter;
import org.apache.commons.cli.Option;
import org.apache.commons.cli.OptionBuilder;
import org.apache.commons.cli.Options;
import org.apache.commons.io.FileUtils;
import org.apache.commons.io.FilenameUtils;
import org.apache.commons.lang3.StringUtils;

/**
 * A factory class to create token files for given text files and annotation files.
 * 
 * @author Jun Araki
 */
public class TokenFileMaker {

  private static final String CLASS_NAME = TokenFileMaker.class.getCanonicalName();

  private static final String LINE_BREAK = System.getProperty("line.separator");

  /** A file extension of a brat annotation file */
  private static final String ANNOTATION_FILE_EXTENSION = "ann";

  /** A file extension of a token (output) file */
  private static final String OUTPUT_FILE_EXTENSION = "tab";

  private String separatorChars;

  /**
   * Public constructor.
   * 
   * @param separatorChars
   */
  public TokenFileMaker(String separatorChars) {
    this.separatorChars = separatorChars;
  }

  /**
   * Aligns the given tokens with the given event mention spans.
   * 
   * @param tokens
   * @param evmSpans
   * @return
   */
  private List<Token> alignTokens(List<Token> tokens, List<EventMentionSpan> evmSpans) {
    Collections.sort(tokens);
    Collections.sort(evmSpans);

    // Initialize.
    List<Token> alignedTokens = new ArrayList<Token>();
    int evmSpansIndex = 0;
    int numEvmSpans = evmSpans.size();

    for (Token token : tokens) {
      // Loop for tokens.

      int tokenBegin = token.getBegin();
      int tokenEnd = token.getEnd();
      for (int i = evmSpansIndex; i < numEvmSpans; i++) {
        EventMentionSpan evmSpan = evmSpans.get(i);
        Document doc = evmSpan.getDocument();
        int evmSpanBegin = evmSpan.getBegin();
        int evmSpanEnd = evmSpan.getEnd();

        if (evmSpanBegin >= tokenEnd) {
          // Case 1
          // If the token precedes the event mention span completely, then we should stop here
          // because the token is fine, and we don't need to examine the other event mention spans.
          alignedTokens.add(token);
          evmSpansIndex = i;
          break;
        }

        if (evmSpanEnd <= tokenBegin) {
          // Case 2
          // If the event mention span precedes the token completely, then we should move on to the
          // next event mention span.
          continue;
        }

        if (evmSpanBegin <= tokenBegin && evmSpanEnd >= tokenEnd) {
          // Case 3
          // If the token is completely covered by the event mention span, then we should stop here
          // because the token is fine, and we don't need to examine the other event mention spans.
          alignedTokens.add(token);
          evmSpansIndex = i;
          break;
        }

        if (evmSpanBegin >= tokenBegin && evmSpanEnd <= tokenEnd) {
          // Case 4
          // If the event mention span is completely covered by the token, then we should split the
          // token into three.
          Logger.warn("Boundary mismatch found in " + doc.getDocId() + ": " + token + " vs. "
                  + evmSpan);

          // Split the token.
          if (evmSpanBegin > tokenBegin) {
            alignedTokens.add(new Token(doc, tokenBegin, evmSpanBegin));
          }
          if (evmSpanBegin < evmSpanEnd) {
            alignedTokens.add(new Token(doc, evmSpanBegin, evmSpanEnd));
          }
          if (evmSpanEnd < tokenEnd) {
            alignedTokens.add(new Token(doc, evmSpanEnd, tokenEnd));
          }

          evmSpansIndex = i;
          break;
        }

        if (evmSpanBegin > tokenBegin && evmSpanBegin < tokenEnd) {
          // Case 5
          // If the beginning of the event mention span exists in the middle of the token, then we
          // should split the token into two.
          Logger.warn("Boundary mismatch found in " + doc.getDocId() + ": " + token + " vs. "
                  + evmSpan);

          // Split the token.
          alignedTokens.add(new Token(doc, tokenBegin, evmSpanBegin));
          alignedTokens.add(new Token(doc, evmSpanBegin, tokenEnd));

          evmSpansIndex = i;
          break;
        }

        if (evmSpanEnd > tokenEnd && evmSpanEnd < tokenEnd) {
          // Case 6
          // If the end of the event mention span exists in the middle of the token, then we should
          // split the token into two.
          Logger.warn("Boundary mismatch found in " + doc.getDocId() + ": " + token + " vs. "
                  + evmSpan);

          // Split the token.
          alignedTokens.add(new Token(doc, tokenBegin, evmSpanEnd));
          alignedTokens.add(new Token(doc, evmSpanEnd, tokenEnd));

          evmSpansIndex = i;
          break;
        }

        // The loop should not reach this point.
        throw new RuntimeException(
                "Unexpected boundary relation between a token and an event mention: " + token
                        + " / " + evmSpan);
      }
    }

    return alignedTokens;
  }

  /**
   * Creates a content of a token file for the given text file.
   * 
   * @param textFile
   * @param annFile
   * @return
   * @throws IOException
   */
  public String create(File textFile, File annFile) throws IOException {
    String text = FileUtils.readFileToString(textFile);
    List<Token> sysTokens = Tokenizer.tokenizeWithOffset(text, separatorChars);
    List<EventMentionSpan> evmSpans = BratAnnotationFileReader.readFile(textFile, annFile);
    List<Token> tokens = alignTokens(sysTokens, evmSpans);

    StringBuilder buf = new StringBuilder();
    for (int i = 0; i < tokens.size(); i++) {
      Token token = tokens.get(i);

      buf.append(i + 1); // token ID
      buf.append("\t");
      buf.append(token.getCoveredText()); // token
      buf.append("\t");
      buf.append(token.getBegin()); // begin
      buf.append("\t");
      buf.append(token.getEnd()); // end
      buf.append(LINE_BREAK);
    }

    return buf.toString();
  }

  /**
   * Creates token files against a collection of input text files with the given file extension
   * under the given directory. This method assumes that all input text files exist under the given
   * directory only, and they do not in any sub-directories.
   * 
   * @param textDir
   * @param textFileExt
   * @param annDir
   * @param outputDir
   */
  public void createFiles(File textDir, String textFileExt, File annDir, File outputDir)
          throws IOException {
    // Extract all text files.
    List<File> textFiles = new ArrayList<File>(FileUtils.listFiles(textDir,
            new String[] { textFileExt }, true));
    List<File> annFiles = new ArrayList<File>(FileUtils.listFiles(annDir,
            new String[] { ANNOTATION_FILE_EXTENSION }, true));
    checkFilePairs(textFiles, textFileExt, annFiles, ANNOTATION_FILE_EXTENSION);

    for (int i = 0; i < textFiles.size(); i++) {
      File textFile = textFiles.get(i);
      File annFile = annFiles.get(i);

      String tokenFileContent = create(textFile, annFile);

      // A token file has the same base name as its corresponding text file with a different file
      // extension.
      String fileName = FilenameUtils.removeExtension(textFile.getName()) + "."
              + OUTPUT_FILE_EXTENSION;
      File outputFile = new File(outputDir, fileName);
      FileUtils.writeStringToFile(outputFile, tokenFileContent);
    }
  }

  /**
   * Throws an exception if the given text files and annotation files are not a valid pair of files
   * with corresponding names.
   * 
   * @param textFiles
   * @param textFileExt
   * @param annFiles
   * @param annFileExt
   * @return
   */
  public void checkFilePairs(List<File> textFiles, String textFileExt, List<File> annFiles,
          String annFileExt) {
    int numTextFiles = textFiles.size();
    int numAnnFiles = annFiles.size();
    if (numTextFiles != numAnnFiles) {
      throw new IllegalArgumentException("The number of text files " + numTextFiles
              + " and that of annotation files are different.");
    }

    Collections.sort(textFiles);
    Collections.sort(annFiles);
    for (int i = 0; i < numTextFiles; i++) {
      File textFile = textFiles.get(i);
      File annFile = annFiles.get(i);

      String textFileBaseName = StringUtils.removeEnd(FilenameUtils.getName(textFile.getName()),
              "." + textFileExt);
      String annFileBaseName = StringUtils.removeEnd(FilenameUtils.getName(annFile.getName()), "."
              + annFileExt);

      if (!textFileBaseName.equals(annFileBaseName)) {
        throw new IllegalArgumentException("The base name of a text file (" + textFileBaseName
                + ") is different from that of an annotation file (" + annFileBaseName + ").");
      }
    }
  }

  public static void main(String[] args) {
    CommandLineParser parser = new BasicParser();

    Options options = new Options();
    @SuppressWarnings("static-access")
    Option optHelp = OptionBuilder.withArgName("help").isRequired(false)
            .withDescription("print this message").create("h");
    @SuppressWarnings("static-access")
    Option optTextDir = OptionBuilder.withArgName("text").isRequired(true).hasArg()
            .withDescription("text directory").create("t");
    @SuppressWarnings("static-access")
    Option optTextFileExt = OptionBuilder.withArgName("extension").isRequired(true).hasArg()
            .withDescription("text file extension").create("e");
    @SuppressWarnings("static-access")
    Option optAnnDir = OptionBuilder.withArgName("annotation").isRequired(true).hasArg()
            .withDescription("annotation directory").create("a");
    @SuppressWarnings("static-access")
    Option optSepChars = OptionBuilder.withArgName("separator").isRequired(false).hasArg()
            .withDescription("separator chars for tokenization").create("s");
    @SuppressWarnings("static-access")
    Option optOutputDir = OptionBuilder.withArgName("output").isRequired(true).hasArg()
            .withDescription("output directory").create("o");

    options.addOption(optHelp);
    options.addOption(optTextDir);
    options.addOption(optTextFileExt);
    options.addOption(optAnnDir);
    options.addOption(optSepChars);
    options.addOption(optOutputDir);

    String textDirPath = null;
    String textFileExt = null;
    String annDirPath = null;
    String separatorChars = "/-\\";  // Default
    String outputDirPath = null;
    try {
      CommandLine cmd = parser.parse(options, args);

      textDirPath = cmd.getOptionValue(optTextDir.getOpt());
      textFileExt = cmd.getOptionValue(optTextFileExt.getOpt());
      annDirPath = cmd.getOptionValue(optAnnDir.getOpt());
      if (cmd.getOptionValue(optSepChars.getOpt()) != null) {
        separatorChars = cmd.getOptionValue(optSepChars.getOpt());
      }
      outputDirPath = cmd.getOptionValue(optOutputDir.getOpt());

    } catch (Exception e) {
      HelpFormatter formatter = new HelpFormatter();
      formatter.printHelp("java " + CLASS_NAME, options, true);
      System.exit(1);
    }

    try {
      File textDir = new File(textDirPath);
      File annDir = new File(annDirPath);
      File outputDir = new File(outputDirPath);
      if (!outputDir.exists()) {
        outputDir.mkdir();
      }

      TokenFileMaker factory = new TokenFileMaker(separatorChars);
      factory.createFiles(textDir, textFileExt, annDir, outputDir);

    } catch (Exception e) {
      e.printStackTrace();
      Logger.error("Stopped due to an error.");
      System.exit(1);
    }

    Logger.info("Successfully completed.");
  }

}
