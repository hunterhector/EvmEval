package net.junaraki.annobase.type.relation.concept;

import net.junaraki.annobase.AnnotationBase;
import net.junaraki.annobase.type.concept.Event;
import net.junaraki.annobase.type.element.EventMention;

/**
 * This class represents a subevent relation between two events. Arg1 is a parent, and arg2 is its
 * child.
 * 
 * @author Jun Araki
 */
public class Subevent extends EventRelation implements Comparable<Subevent> {

  private static final long serialVersionUID = 1237483711974714467L;

  /**
   * Public constructor.
   * 
   * @param annBase
   */
  public Subevent(AnnotationBase annBase) {
    super(annBase);
  }

  @Override
  public String toString() {
    Event parent = getParent();
    Event child = getChild();
    return String.format("%s: %s --> %s", getTypeName(), parent.toShortString(),
            child.toShortString());
  }

  /**
   * An element annotation precedes another one if the former's begin precedes the latter's, or the
   * former's end precedes the latter's if the former's begin is equal to the latter's.
   * 
   * @param that
   */
  @Override
  public int compareTo(Subevent that) {
    Event thisParent = getParent();
    Event thatParent = that.getParent();
    Event thisChild = getChild();
    Event thatChild = that.getChild();
    thisParent.sortEventMentions();
    thatParent.sortEventMentions();
    thisChild.sortEventMentions();
    thatChild.sortEventMentions();

    EventMention thisFirstParent = thisParent.getEventMentionAt(0);
    EventMention thatFirstParent = thatParent.getEventMentionAt(0);
    EventMention thisFirstChild = thisChild.getEventMentionAt(0);
    EventMention thatFirstChild = thatChild.getEventMentionAt(0);

    int compare = thisFirstParent.compareTo(thatFirstParent);
    if (compare == 0) {
      compare = thisFirstChild.compareTo(thatFirstChild);
    }

    return compare;
  }

  public Event getParent() {
    return getFrom();
  }

  public void setParent(Event parent) {
    setFrom(parent);
  }

  public Event getChild() {
    return getTo();
  }

  public void setChild(Event child) {
    setTo(child);
  }

}
