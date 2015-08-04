package net.junaraki.annobase.io;

import java.io.File;
import java.util.List;

import net.junaraki.annobase.AnnotationBase;

public interface Writer {

  /**
   * Writes the given annotation base instance to the given file.
   * 
   * @param annBase
   * @param file
   */
  public void write(AnnotationBase annBase, File file) throws Exception;

  /**
   * Writes a list of the given annotation base instances to a list of the given files.
   * 
   * @param annBases
   * @param files
   */
  public void write(List<AnnotationBase> annBases, List<File> files) throws Exception;

}
