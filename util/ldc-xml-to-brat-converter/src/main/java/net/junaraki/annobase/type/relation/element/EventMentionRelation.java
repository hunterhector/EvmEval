package net.junaraki.annobase.type.relation.element;

import net.junaraki.annobase.AnnotationBase;
import net.junaraki.annobase.type.element.EventMention;

/**
 * This class represents a relation between two event mentions.
 * 
 * @author Jun Araki
 */
public class EventMentionRelation extends ElementDirectedBinaryRelation {

  private static final long serialVersionUID = 1471590292694561623L;

  /**
   * Public constructor.
   * 
   * @param annBase
   */
  public EventMentionRelation(AnnotationBase annBase) {
    super(annBase);
  }

  @Override
  public EventMention getFrom() {
    return (EventMention) super.getFrom();
  }

  public void setFrom(EventMention from) {
    super.setFrom(from);
  }

  @Override
  public EventMention getTo() {
    return (EventMention) super.getTo();
  }

  public void setTo(EventMention to) {
    super.setTo(to);
  }

}
