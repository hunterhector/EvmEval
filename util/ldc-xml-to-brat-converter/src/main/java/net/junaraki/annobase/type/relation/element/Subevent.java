package net.junaraki.annobase.type.relation.element;

import net.junaraki.annobase.AnnotationBase;
import net.junaraki.annobase.type.element.EventMention;

/**
 * This class represents a subevent relation between two event mentions. Arg1 is a parent, and arg2
 * is its child.
 * 
 * @author Jun Araki
 */
public class Subevent extends EventMentionRelation {

  private static final long serialVersionUID = -6391412702042994016L;

  /**
   * Public constructor.
   * 
   * @param annBase
   */
  public Subevent(AnnotationBase annBase) {
    super(annBase);
  }

  public EventMention getParent() {
    return getFrom();
  }

  public void setParent(EventMention parent) {
    setFrom(parent);
  }

  public EventMention getChild() {
    return getTo();
  }

  public void setChild(EventMention child) {
    setTo(child);
  }

}
