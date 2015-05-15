package evmeval;

import com.google.common.base.Splitter;
import org.apache.commons.collections4.CollectionUtils;
import org.apache.commons.io.FileUtils;
import org.apache.commons.io.FilenameUtils;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

/**
 * This class parses a given brat annotation file, and extracts event mention spans. See the URL
 * below about the format of the annotation file.
 *
 * @author Jun Araki
 * @see http://brat.nlplab.org/standoff.html
 */
public class BratAnnotationFileReader {

    /**
     * The prefix for annotation
     */
    private static final String ANN_PREFIX = "T";

    /**
     * The prefix for events
     */
    private static final String EVENT_PREFIX = "E";

    /**
     * The prefix for attributes
     */
    private static final String ATTR_PREFIX = "A";

    /**
     * The prefix for notes
     */
    private static final String NOTE_PREFIX = "#";

    private static Splitter wsSplitter;

    private static Splitter tabSplitter;

    private static Splitter semicolonSplitter;

    static {
        wsSplitter = Splitter.on(" ").trimResults();
        tabSplitter = Splitter.on("\t").trimResults();
        semicolonSplitter = Splitter.on(";").trimResults();
    }

    /**
     * Reads the given brat annotation file, and returns a list of event mention spans.
     *
     * @param textFile
     * @param annFile
     * @return
     * @throws IOException
     */
    public static List<EventMentionSpan> readFile(File textFile, File annFile) throws IOException {
        // Initialize.
        List<EventMentionSpan> evmSpans = new ArrayList<EventMentionSpan>(); // A list of event mention spans.

        String text = FileUtils.readFileToString(textFile);
        String docId = FilenameUtils.removeExtension(textFile.getName());
        Document doc = new Document(text, docId);
        List<String> tmpList = null;

        // Parse the annotation file line by line.
        for (String line : FileUtils.readLines(annFile)) {
            List<String> items = tabSplitter.splitToList(line);
            if (CollectionUtils.isEmpty(items)) {
                Logger.warn("Encounter a blank line, will skip it");
//                throw new RuntimeException("Invalid format of a line: " + line);
            }

            String firstItem = items.get(0); // This should specific types of annotation.
            if (firstItem.startsWith(ANN_PREFIX)) {
                tmpList = semicolonSplitter.splitToList(items.get(1));
                int begin, end;
                List<String> tmpList2 = null;
                for (int i = 0; i < tmpList.size(); i++) {
                    tmpList2 = wsSplitter.splitToList(tmpList.get(i));
                    if (i == 0) {
                        // tmpList2.get(0) is an event type.
                        begin = Integer.parseInt(tmpList2.get(1));
                        end = Integer.parseInt(tmpList2.get(2));
                    } else {
                        begin = Integer.parseInt(tmpList2.get(0));
                        end = Integer.parseInt(tmpList2.get(1));
                    }

                    // Create a new event mention span.
                    evmSpans.add(new EventMentionSpan(doc, begin, end));
                }
            } else if (firstItem.startsWith(EVENT_PREFIX)) {
                // Found an event type of an event mention.

                // Do nothing.
            } else if (firstItem.startsWith(ATTR_PREFIX)) {
                // Found realis of an event mention.

                // Do nothing.
            } else if (firstItem.startsWith(NOTE_PREFIX)) {
                // Found annotator notes of an event mention.
                // Do nothing.
            } else if (firstItem.startsWith("")) {
                // Found coreference
                // Do nothing
            } else {
                Logger.warn("Unknown annotation found, will omit the following line: ");
                Logger.log(line);
//                throw new RuntimeException("Invalid format of a line: " + line);
            }
        }

        return evmSpans;
    }

}
