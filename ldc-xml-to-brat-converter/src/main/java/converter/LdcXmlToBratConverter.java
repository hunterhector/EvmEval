package converter;

import java.io.File;
import java.util.ArrayList;
import java.util.List;

import joptsimple.OptionException;
import joptsimple.OptionParser;
import joptsimple.OptionSet;
import joptsimple.OptionSpec;
import net.junaraki.annobase.pipeline.AbstractPipeline;

public class LdcXmlToBratConverter extends AbstractPipeline {

  public LdcXmlToBratConverter() {
    super();
    reader = new LdcXmlReader();
    writer = new BratWriter();
  }

  public static void main(String[] args) throws Exception {
    OptionParser parser = new OptionParser();
    parser.accepts("h", "help").forHelp();
    OptionSpec<String> optInputDir = parser.accepts("i", "input directory").withRequiredArg()
            .ofType(String.class).describedAs("input dir");
    OptionSpec<String> optOutputDir = parser.accepts("o", "output directory").withRequiredArg()
            .ofType(String.class).describedAs("output dir");

    OptionSet options = null;
    try {
      options = parser.parse(args);

      if (!options.hasOptions()) {
        parser.printHelpOn(System.out);
        return;
      }
    } catch (OptionException e) {
      parser.printHelpOn(System.out);
      return;
    }

    LdcXmlToBratConverter converter = new LdcXmlToBratConverter();
    File inputDir = new File(options.valueOf(optInputDir));
    String[] extensions = new String[] { LdcXmlReader.INPUT_TEXT_FILE_EXT };
    List<File> inputFiles = converter.getReader().collect(inputDir, extensions, false);

    File outputDir = new File(options.valueOf(optOutputDir));
    List<File> outputFiles = new ArrayList<File>();
    for (File inputFile : inputFiles) {
      for (String extension : extensions) {
        String fileName = inputFile.getName();
        if (!fileName.endsWith(extension)) {
          continue;
        }

        String baseFileName = fileName.substring(0, fileName.length() - extension.length() - 1);
        String outputFileName = baseFileName + ".ann";
        outputFiles.add(new File(outputDir, outputFileName));
        break;
      }
    }

    converter.run(inputFiles, outputFiles);
  }

}
