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

  public LdcXmlToBratConverter(File annDir, String textFileExt, String annFileExt, boolean detagText) {
    super();
    reader = new LdcXmlReader(annDir, textFileExt, annFileExt, detagText);
    writer = new BratWriter();
  }

  public static void main(String[] args) throws Exception {
    OptionParser parser = new OptionParser();
    parser.accepts("h", "help").forHelp();
    OptionSpec<String> optTextDir = parser.accepts("t", "text directory").withRequiredArg()
            .ofType(String.class).describedAs("text dir");
    OptionSpec<String> optTextFileExt = parser.accepts("te", "text file extension")
            .withRequiredArg().ofType(String.class).describedAs("text file extension");
    OptionSpec<String> optAnnDir = parser.accepts("a", "annotation directory").withRequiredArg()
            .ofType(String.class).describedAs("annotation dir");
    OptionSpec<String> optAnnFileExt = parser.accepts("ae", "annotation file extension")
            .withRequiredArg().ofType(String.class).describedAs("annotation file extension");
    OptionSpec<String> optOutputDir = parser.accepts("o", "output directory").withRequiredArg()
            .ofType(String.class).describedAs("output dir");
    OptionSpec<Void> optDetag = parser.accepts("d", "whether to detag text");

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

    File textDir = new File(options.valueOf(optTextDir));
    String textFileExt = options.valueOf(optTextFileExt);
    File annDir = new File(options.valueOf(optAnnDir));
    String annFileExt = options.valueOf(optAnnFileExt);
    boolean detagText = options.has(optDetag);
    LdcXmlToBratConverter converter = new LdcXmlToBratConverter(annDir, textFileExt, annFileExt, detagText);
    String[] extensions = new String[] { textFileExt };
    List<File> inputFiles = converter.getReader().collect(textDir, extensions, false);

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
