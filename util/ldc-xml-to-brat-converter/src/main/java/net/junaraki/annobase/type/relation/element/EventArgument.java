package net.junaraki.annobase.type.relation.element;

import net.junaraki.annobase.AnnotationBase;
import net.junaraki.annobase.type.element.EntityMention;
import net.junaraki.annobase.type.element.EventMention;

/**
 * This class represents an event argument annotation. An event argument defined as is a directed
 * binary relation from an event mention to an entity mention.
 * 
 * @author Jun Araki
 */
public class EventArgument extends ElementDirectedBinaryRelation {

  private static final long serialVersionUID = 8157314130052319673L;

  /**
   * Public constructor.
   * 
   * @param annBase
   */
  public EventArgument(AnnotationBase annBase) {
    super(annBase);
  }

  public String getRole() {
    return relationType;
  }

  public void setRole(String role) {
    this.relationType = role;
  }

  @Override
  public EventMention getFrom() {
    return (EventMention) super.getFrom();
  }

  public void setFrom(EventMention from) {
    super.setFrom(from);
  }

  @Override
  public EntityMention getTo() {
    return (EntityMention) super.getTo();
  }

  public void setTo(EntityMention to) {
    super.setTo(to);
  }

}
