package converter;

import com.google.common.io.Files;
import joptsimple.OptionException;
import joptsimple.OptionParser;
import joptsimple.OptionSet;
import joptsimple.OptionSpec;
import net.junaraki.annobase.AnnotationBase;
import net.junaraki.annobase.pipeline.AbstractPipeline;
import org.apache.commons.io.FileUtils;

import java.io.File;
import java.util.ArrayList;
import java.util.List;

public class RichEreToTbfConverter extends AbstractPipeline {

    public RichEreToTbfConverter(File annDir, String textFileExt, String annFileExt, String inputMode) {
        super();
        reader = new LdcXmlReader(annDir, textFileExt, annFileExt, false, inputMode) {
            @Override
            protected AnnotationBase consume(AnnotationBase annBase, String docText, String baseName) {
                TbfAnnotationBase annoBase = new TbfAnnotationBase(docText, baseName);
                annoBase.consume(annBase);
                return annoBase;
            }
        };
        writer = new TbfWriter();
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
        OptionSpec<String> optOutputFile = parser.accepts("o", "output file").withRequiredArg()
                .ofType(String.class).describedAs("output file");
//        OptionSpec<String> optOutputDir = parser.accepts("d", "output directory").withRequiredArg()
//                .ofType(String.class).describedAs("output dir");
        OptionSpec<String> optInputMode = parser.accepts("i", "input mode (\"event-nugget\")")
                .withRequiredArg().ofType(String.class).describedAs("input mode");

        OptionSet options = null;
        try {
            options = parser.parse(args);

            if (!options.hasOptions() || options.has("h")) {
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
        String inputMode = options.valueOf(optInputMode);
        if (inputMode != null && !inputMode.equals(LdcXmlReader.INPUT_MODE_EVENT_NUGGET)) {
            Logger.error(String.format("Invalid input mode: %s", inputMode));
            return;
        }

        RichEreToTbfConverter converter = new RichEreToTbfConverter(annDir, textFileExt, annFileExt, inputMode);
        String[] extensions = new String[]{textFileExt};
        List<File> inputFiles = converter.getReader().collect(textDir, extensions, false);

        Logger.info(String.format("There are %d files to be processed.", inputFiles.size()));

        File outputDir = Files.createTempDir();
        List<File> outputFiles = new ArrayList<>();
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

        File finalOutputFile = new File(options.valueOf(optOutputFile));
        boolean append = false;
        for (File outputFile : outputFiles) {
            FileUtils.write(finalOutputFile, FileUtils.readFileToString(outputFile), append);
            append = true;
        }

        Logger.info("Finished the conversion from LDC XML data to TBF data.");
    }
}
