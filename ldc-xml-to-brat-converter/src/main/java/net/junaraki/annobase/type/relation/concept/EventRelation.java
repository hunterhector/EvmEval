package net.junaraki.annobase.type.relation.concept;

import net.junaraki.annobase.AnnotationBase;
import net.junaraki.annobase.type.concept.Event;

/**
 * This class represents a relation between two events.
 * 
 * @author Jun Araki
 *
 */
public class EventRelation extends ConceptDirectedBinaryRelation {

  private static final long serialVersionUID = 4384934708760040258L;

  /**
   * Public constructor.
   * 
   * @param annBase
   */
  public EventRelation(AnnotationBase annBase) {
    super(annBase);
  }

  @Override
  public Event getFrom() {
    return (Event) super.getFrom();
  }

  public void setFrom(Event from) {
    super.setFrom(from);
  }

  @Override
  public Event getTo() {
    return (Event) super.getTo();
  }

  public void setTo(Event to) {
    super.setTo(to);
  }

}
