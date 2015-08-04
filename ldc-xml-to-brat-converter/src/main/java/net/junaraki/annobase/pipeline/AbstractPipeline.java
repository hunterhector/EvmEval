package net.junaraki.annobase.pipeline;

import java.io.File;
import java.util.ArrayList;
import java.util.List;

import net.junaraki.annobase.AnnotationBase;
import net.junaraki.annobase.io.Reader;
import net.junaraki.annobase.io.Writer;
import net.junaraki.annobase.process.Processor;

public abstract class AbstractPipeline implements Pipeline {

  protected Reader reader;

  protected Writer writer;

  protected List<Processor> processors;

  /**
   * Public constructor.
   */
  public AbstractPipeline() {
    processors = new ArrayList<Processor>();
  }

  /**
   * Public constructor.
   * 
   * @param reader
   * @param writer
   */
  public AbstractPipeline(Reader reader, Writer writer) {
    this.reader = reader;
    this.writer = writer;
    processors = new ArrayList<Processor>();
  }

  /**
   * Public constructor.
   * 
   * @param processors
   */
  public AbstractPipeline(List<Processor> processors) {
    this.processors = processors;
  }

  /**
   * Public constructor.
   * 
   * @param reader
   * @param writer
   * @param processors
   */
  public AbstractPipeline(Reader reader, Writer writer, List<Processor> processors) {
    this.reader = reader;
    this.writer = writer;
    this.processors = processors;
  }

  /**
   * Runs this pipeline against the given files.
   * 
   * @param inputFiles
   * @param outputFiles
   */
  public void run(List<File> inputFiles, List<File> outputFiles) throws Exception {
    List<AnnotationBase> annBases = reader.read(inputFiles);
    for (AnnotationBase annBase : annBases) {
      String docId = annBase.getSourceDocument().getId();
      System.out.println(String.format("[INFO] Processing document %s", docId));

      for (Processor processor : processors) {
        processor.process(annBase);
      }
    }
    writer.write(annBases, outputFiles);
  }

  public Reader getReader() {
    return reader;
  }

  public void setReader(Reader reader) {
    this.reader = reader;
  }

  public Writer getWriter() {
    return writer;
  }

  public void setWriter(Writer writer) {
    this.writer = writer;
  }

  public List<Processor> getProcessors() {
    return processors;
  }

  public void setProcessors(List<Processor> processors) {
    this.processors = processors;
  }

  /**
   * Adds the given processor to this pipeline.
   * 
   * @param processor
   */
  @Override
  public void addProcessor(Processor processor) {
    processors.add(processor);
  }

}
