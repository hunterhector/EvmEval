package converter;

import net.junaraki.annobase.AnnotationBase;
import net.junaraki.annobase.io.AbstractWriter;
import org.apache.commons.io.FileUtils;

import java.io.File;

/**
 * Created with IntelliJ IDEA.
 * Date: 8/22/16
 * Time: 10:04 PM
 *
 * @author Zhengzhong Liu
 */
public class TbfWriter extends AbstractWriter{

    @Override
    public void write(AnnotationBase annBase, File file) throws Exception {
//        File outputDir = file.getParentFile();
//        String textFileName = annBase.getSourceDocument().getId() + ".txt";
//        File textFile = new File(outputDir, textFileName);
//        FileUtils.write(textFile, annBase.getDocumentText());
        FileUtils.write(file, ((TbfAnnotationBase) annBase).toString());
    }
}
