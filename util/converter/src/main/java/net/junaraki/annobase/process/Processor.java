package net.junaraki.annobase.process;

import net.junaraki.annobase.AnnotationBase;

public interface Processor {

  /**
   * Carries out a certain process against the given annotation base instance.
   * 
   * @param annBase
   */
  public void process(AnnotationBase annBase);

}
