package net.junaraki.annobase.type.element;

import net.junaraki.annobase.AnnotationBase;

/**
 * This class represents an event mention candidate, which manages just a text boundary for an event
 * mention ignoring other information such as attributes and arguments.
 * 
 * @author Jun Araki
 */
public class EventMentionCandidate extends TokenBasedTextSpan {

  private static final long serialVersionUID = 8962230337953555503L;

  /**
   * Public constructor.
   * 
   * @param annBase
   * @param begin
   * @param end
   */
  public EventMentionCandidate(AnnotationBase annBase, int begin, int end) {
    super(annBase, begin, end);
  }

}
