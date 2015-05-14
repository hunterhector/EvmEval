package net.junaraki.annobase.process;

import net.junaraki.annobase.AnnotationBase;

public abstract class AbstractProcessor implements Processor {

  @Override
  public abstract void process(AnnotationBase annBase);

}
