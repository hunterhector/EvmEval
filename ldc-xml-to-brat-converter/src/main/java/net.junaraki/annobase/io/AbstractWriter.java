package net.junaraki.annobase.io;

import java.io.File;
import java.util.List;

import net.junaraki.annobase.AnnotationBase;

public abstract class AbstractWriter implements Writer {

  public static final String DEFAULT_OUTPUT_DIR = "out";

  /**
   * Writes the given annotation base instance to the given file.
   * 
   * @param annBase
   * @param file
   */
  @Override
  public abstract void write(AnnotationBase annBase, File file) throws Exception;

  /**
   * Writes a list of the given annotation base instances to a list of the given files.
   * 
   * @param annBases
   * @param files
   */
  @Override
  public void write(List<AnnotationBase> annBases, List<File> files) throws Exception {
    for (int i = 0; i < files.size(); i++) {
      write(annBases.get(i), files.get(i));
    }
  }

}
