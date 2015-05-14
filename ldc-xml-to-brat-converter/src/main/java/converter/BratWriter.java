package converter;

import java.io.File;

import org.apache.commons.io.FileUtils;

import net.junaraki.annobase.AnnotationBase;
import net.junaraki.annobase.io.AbstractWriter;

public class BratWriter extends AbstractWriter {

  @Override
  public void write(AnnotationBase annBase, File file) throws Exception {
    // Output a text file.
    File outputDir = file.getParentFile();
    String textFileName = annBase.getSourceDocument().getId() + ".txt";
    File textFile = new File(outputDir, textFileName);
    FileUtils.write(textFile, annBase.getDocumentText());

    // Output an annotation file.
    FileUtils.write(file, ((BratAnnotationBase) annBase).toString());
  }

}
