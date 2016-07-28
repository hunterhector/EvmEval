package evmeval;

import com.google.common.base.Splitter;
import com.google.common.collect.BiMap;
import org.apache.commons.cli.*;
import org.apache.commons.collections4.CollectionUtils;
import org.apache.commons.io.FileUtils;
import org.apache.commons.io.FilenameUtils;
import org.apache.commons.lang3.StringUtils;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

/**
 * Converts annotation via token map files.
 * 
 * @author Jun Araki
 */
public class AnnotationConverter {

  private static final String CLASS_NAME = TokenFileMaker.class.getCanonicalName();

  private static final String LINE_BREAK = System.getProperty("line.separator");

  /** A file extension of a brat annotation file */
  private static final String ANNOTATION_FILE_EXTENSION = "ann";

  /** A file extension of a token map file */
  private static final String TOKEN_MAP_FILE_EXTENSION = "txt.tab";

  /** A file extension of a output file */
  private static final String OUTPUT_FILE_EXTENSION = "tkn.ann";

  /** The prefix for annotation */
  private static final String ANN_PREFIX = "T";

  private TokenMapFileReader tokenMapReader;

  private Splitter wsSplitter;

  private Splitter tabSplitter;

  private Splitter semicolonSplitter;

  public AnnotationConverter() {
    tokenMapReader = new TokenMapFileReader();
    wsSplitter = Splitter.on(" ");
    tabSplitter = Splitter.on("\t");
    semicolonSplitter = Splitter.on(";");
  }

  /**
   * Creates a new annotation file for the given annotation file and token map file.
   * 
   * @param textDir
   * @param textFileExt
   * @param annDir
   * @param tokenMapDir
   * @param outputDir
   * @throws IOException
   */
  public void convertFiles(File textDir, String textFileExt, File annDir, File tokenMapDir,
          File outputDir) throws IOException {
    // Extract all text files.
    List<File> textFiles = new ArrayList<File>(FileUtils.listFiles(textDir,
            new String[] { textFileExt }, true));
    List<File> annFiles = new ArrayList<File>(FileUtils.listFiles(annDir,
            new String[] { ANNOTATION_FILE_EXTENSION }, true));
    List<File> tokenMapFiles = new ArrayList<File>(FileUtils.listFiles(annDir,
            new String[] { TOKEN_MAP_FILE_EXTENSION }, true));
    checkFiles(textFiles, textFileExt, annFiles, ANNOTATION_FILE_EXTENSION, tokenMapFiles,
            TOKEN_MAP_FILE_EXTENSION);

    for (int i = 0; i < textFiles.size(); i++) {
      File textFile = textFiles.get(i);
      File annFile = annFiles.get(i);
      File tokenMapFile = tokenMapFiles.get(i);

      String annFileContent = convertFile(annFile, tokenMapFile);

      // A token file has the same base name as its corresponding text file with a different file
      // extension.
      String fileName = FilenameUtils.removeExtension(textFile.getName()) + "."
              + OUTPUT_FILE_EXTENSION;
      File outputFile = new File(outputDir, fileName);
      FileUtils.writeStringToFile(outputFile, annFileContent);
    }
  }

  /**
   * Returns a content of a new annotation file for the given annotation file and token map file.
   * 
   * @param annFile
   * @param tokenMapFile
   * @return
   * @throws IOException
   */
  public String convertFile(File annFile, File tokenMapFile) throws IOException {
    tokenMapReader.readFile(tokenMapFile);
    BiMap<Integer, Integer> beginOffsetMap = tokenMapReader.getBeginOffsetMap();
    BiMap<Integer, Integer> endOffsetMap = tokenMapReader.getEndOffsetMap();

    StringBuilder buf = new StringBuilder();
    for (String line : FileUtils.readLines(annFile)) {
      List<String> values = tabSplitter.splitToList(line);
      if (CollectionUtils.isEmpty(values)) {
        throw new RuntimeException("Invalid format of a line: " + line);
      }

      String firstValue = values.get(0);
      if (!firstValue.startsWith(ANN_PREFIX)) {
        // In the case of annotation without begin/end offsets
        buf.append(line);
        buf.append(LINE_BREAK);
        continue;
      }

      // In the case of annotation with begin/end offsets
      String secondValue = values.get(1);
      String thridValue = values.get(2);

      buf.append(firstValue);
      buf.append("\t");

      List<String> tmpList = semicolonSplitter.splitToList(secondValue);
      for (int i = 0; i < tmpList.size(); i++) {
        List<String> tmpList2 = wsSplitter.splitToList(tmpList.get(i));
        int beginIndex, endIndex;
        if (i == 0) {
          // tmpList2.get(0) is an event type.
          beginIndex = 1;
          endIndex = 2;

          buf.append(tmpList2.get(0));
          buf.append(" ");
        } else {
          beginIndex = 0;
          endIndex = 1;

          buf.append(";");
        }

        int begin = Integer.parseInt(tmpList2.get(beginIndex));
        int end = Integer.parseInt(tmpList2.get(endIndex));

        int beginNew, endNew;
        if (beginOffsetMap.containsKey(begin)) {
          beginNew = beginOffsetMap.get(begin);
        } else {
          throw new RuntimeException("No new begin offset found for " + begin);
        }
        if (endOffsetMap.containsKey(end)) {
          endNew = endOffsetMap.get(end);
        } else {
          throw new RuntimeException("No new end offset found for " + end);
        }

        buf.append(beginNew);
        buf.append(" ");
        buf.append(endNew);
      }
      buf.append("\t");

      buf.append(thridValue);
      buf.append(LINE_BREAK);
    }

    return buf.toString();
  }

  /**
   * Throws an exception if the given text files and annotation files are not a valid pair of files
   * with corresponding names.
   * 
   * @param textFiles
   * @param textFileExt
   * @param annFiles
   * @param annFileExt
   * @param tokenMapFiles
   * @param tokenMapFileExt
   * @return
   */
  public void checkFiles(List<File> textFiles, String textFileExt, List<File> annFiles,
          String annFileExt, List<File> tokenMapFiles, String tokenMapFileExt) {
    int numTextFiles = textFiles.size();
    int numAnnFiles = annFiles.size();
    int numTokenMapFiles = tokenMapFiles.size();
    if (numTextFiles != numAnnFiles) {
      throw new IllegalArgumentException("The number of text files " + numTextFiles
              + " and that of annotation files are different.");
    }
    if (numTextFiles != numTokenMapFiles) {
      throw new IllegalArgumentException("The number of text files " + numTextFiles
              + " and that of token map files are different.");
    }

    Collections.sort(textFiles);
    Collections.sort(annFiles);
    Collections.sort(tokenMapFiles);
    for (int i = 0; i < numTextFiles; i++) {
      File textFile = textFiles.get(i);
      File annFile = annFiles.get(i);
      File tokenMapFile = tokenMapFiles.get(i);

      String textFileBaseName = StringUtils.removeEnd(FilenameUtils.getName(textFile.getName()),
              "." + textFileExt);
      String annFileBaseName = StringUtils.removeEnd(FilenameUtils.getName(annFile.getName()), "."
              + annFileExt);
      String tokenMapFileBaseName = StringUtils.removeEnd(
              FilenameUtils.getName(tokenMapFile.getName()), "." + tokenMapFileExt);

      if (!textFileBaseName.equals(annFileBaseName)) {
        throw new IllegalArgumentException("The base name of a text file (" + textFileBaseName
                + ") is different from that of an annotation file (" + annFileBaseName + ").");
      }
      if (!textFileBaseName.equals(tokenMapFileBaseName)) {
        throw new IllegalArgumentException("The base name of a text file (" + textFileBaseName
                + ") is different from that of an annotation file (" + tokenMapFileBaseName + ").");
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
    Option optTokenMapDir = OptionBuilder.withArgName("evmeval").isRequired(true).hasArg()
            .withDescription("token map directory").create("tm");
    @SuppressWarnings("static-access")
    Option optOutputDir = OptionBuilder.withArgName("output").isRequired(true).hasArg()
            .withDescription("output directory").create("o");

    options.addOption(optHelp);
    options.addOption(optTextDir);
    options.addOption(optTextFileExt);
    options.addOption(optAnnDir);
    options.addOption(optTokenMapDir);
    options.addOption(optOutputDir);

    String textDirPath = null;
    String textFileExt = null;
    String annDirPath = null;
    String tokenMapDirPath = null;
    String outputDirPath = null;
    try {
      CommandLine cmd = parser.parse(options, args);

      textDirPath = cmd.getOptionValue(optTextDir.getOpt());
      textFileExt = cmd.getOptionValue(optTextFileExt.getOpt());
      annDirPath = cmd.getOptionValue(optAnnDir.getOpt());
      tokenMapDirPath = cmd.getOptionValue(optTokenMapDir.getOpt());
      outputDirPath = cmd.getOptionValue(optOutputDir.getOpt());

    } catch (Exception e) {
      HelpFormatter formatter = new HelpFormatter();
      formatter.printHelp("java " + CLASS_NAME, options, true);
      System.exit(1);
    }

    try {
      File textDir = new File(textDirPath);
      File annDir = new File(annDirPath);
      File tokenMapDir = new File(tokenMapDirPath);
      File outputDir = new File(outputDirPath);
      if (!outputDir.exists()) {
        outputDir.mkdir();
      }

      AnnotationConverter ac = new AnnotationConverter();
      ac.convertFiles(textDir, textFileExt, annDir, tokenMapDir, outputDir);

    } catch (Exception e) {
      e.printStackTrace();
      Logger.error("Stopped due to an error.");
      System.exit(1);
    }

    Logger.info("Successfully completed.");
  }

}
