package net.junaraki.annobase.io;

import java.io.File;
import java.util.ArrayList;
import java.util.List;

import org.apache.commons.io.FileUtils;

import net.junaraki.annobase.AnnotationBase;

public abstract class AbstractReader implements Reader {

  /**
   * Reads the given file, and returns an annotation base instance.
   * 
   * @param file
   * @return
   */
  @Override
  public abstract AnnotationBase read(File file) throws Exception;

  /**
   * Reads a list of the given files, and returns a list of annotation base instances.
   * 
   * @param files
   * @return
   */
  @Override
  public List<AnnotationBase> read(List<File> files) throws Exception {
    List<AnnotationBase> annBases = new ArrayList<AnnotationBase>();
    for (File file : files) {
      annBases.add(read(file));
    }
    return annBases;
  }

  /**
   * Reads a list of files from the given directory with the given extensions, and returns a list of
   * annotation base instances.
   * 
   * @param directory
   * @param extensions
   * @param recursive
   * @return
   */
  @Override
  public List<File> collect(File directory, String[] extensions, boolean recursive) {
    return new ArrayList<File>(FileUtils.listFiles(directory, extensions, recursive));
  }

}
