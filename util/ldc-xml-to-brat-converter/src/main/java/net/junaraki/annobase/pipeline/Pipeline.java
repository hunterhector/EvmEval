package net.junaraki.annobase.pipeline;

import net.junaraki.annobase.process.Processor;

public interface Pipeline {

  /**
   * Adds the given processor to this pipeline.
   * 
   * @param processor
   */
  public void addProcessor(Processor processor);

}
