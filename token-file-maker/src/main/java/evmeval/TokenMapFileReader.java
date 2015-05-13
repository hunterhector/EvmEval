package evmeval;

import java.io.File;
import java.io.IOException;
import java.util.List;

import org.apache.commons.collections4.CollectionUtils;
import org.apache.commons.io.FileUtils;

import com.google.common.base.Splitter;
import com.google.common.collect.BiMap;
import com.google.common.collect.HashBiMap;

import edu.stanford.nlp.util.StringUtils;

/**
 * This class parses a given brat annotation file, and extracts event mention spans. See the URL
 * below about the format of the annotation file.
 * 
 * @see http://brat.nlplab.org/standoff.html
 * @author Jun Araki
 */
public class TokenMapFileReader {

  private BiMap<Integer, Integer> beginOffsetMap;

  private BiMap<Integer, Integer> endOffsetMap;

  private Splitter tabSplitter;

  public TokenMapFileReader() {
    beginOffsetMap = HashBiMap.create();
    endOffsetMap = HashBiMap.create();
    tabSplitter = Splitter.on("\t").trimResults();
  }

  /**
   * Reads the token map file.
   * 
   * @param tokenMapFile
   * @throws IOException
   * @return
   */
  public void readFile(File tokenMapFile) throws IOException {
    // Initialize.
    beginOffsetMap.clear();
    endOffsetMap.clear();

    // Parse the token map file line by line.
    for (String line : FileUtils.readLines(tokenMapFile)) {
      List<String> values = tabSplitter.splitToList(line);
      if (CollectionUtils.isEmpty(values) || values.size() != 6) {
        throw new RuntimeException("Invalid format of a line: " + line);
      }

      String firstValue = values.get(0);
      if ("token_id".equals(firstValue)) {
        // Skip the first line.
        continue;
      }
      if (!"t".equals(firstValue.substring(0, 1))
              || !StringUtils.isNumeric(firstValue.substring(1))) {
        throw new RuntimeException("Invalid format of a line: " + line);
      }

      int beginOld = Integer.valueOf(values.get(2));
      int endOld = Integer.valueOf(values.get(3)) + 1;  // LDC's end offset is inclusive.
      int beginNew = Integer.valueOf(values.get(4));
      int endNew = Integer.valueOf(values.get(5)) + 1;  // LDC's end offset is inclusive.
      if (beginOffsetMap.containsKey(beginOld)) {
        Logger.warn("Duplicated begin offset: " + beginOld + " in " + tokenMapFile);
      }
      if (beginOffsetMap.inverse().containsKey(beginNew)) {
        Logger.warn("Duplicated begin offset: " + beginNew + " in " + tokenMapFile);
      }
      if (endOffsetMap.containsKey(endOld)) {
        Logger.warn("Duplicated end offset: " + endOld + " in " + tokenMapFile);
      }
      if (endOffsetMap.inverse().containsKey(endNew)) {
        Logger.warn("Duplicated end offset: " + endNew + " in " + tokenMapFile);
      }

      beginOffsetMap.put(beginOld, beginNew);
      endOffsetMap.put(endOld, endNew);
    }
  }

  public BiMap<Integer, Integer> getBeginOffsetMap() {
    return beginOffsetMap;
  }

  public BiMap<Integer, Integer> getEndOffsetMap() {
    return endOffsetMap;
  }

}
