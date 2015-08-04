package net.junaraki.annobase.type.concept;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

import net.junaraki.annobase.AnnotationBase;
import net.junaraki.annobase.type.AbstractAnnotation;
import net.junaraki.annobase.type.element.EventMention;
import net.junaraki.annobase.type.relation.concept.EventRelation;

/**
 * This class represents an abstract type of events. Event mentions belonging to an event are
 * coreferential with each other.
 * 
 * @author Jun Araki
 */
public class Event extends AbstractAnnotation implements Comparable<Event> {

  private static final long serialVersionUID = -3566955955996540086L;

  protected String eventType;

  /** A list of event mentions that belong to this event, i.e., coreferential event mentions */
  protected List<EventMention> evms;

  protected List<EventRelation> fromRels;

  protected List<EventRelation> toRels;

  /** Lazily initialized, cached hashCode */
  private volatile int hashCode;

  /**
   * Public constructor.
   * 
   * @param annBase
   */
  public Event(AnnotationBase annBase) {
    super(annBase);
    evms = new ArrayList<EventMention>();
  }

  @Override
  public String toString() {
    String srcDocId = getAnnotationBase().getSourceDocument().getId();
    StringBuilder evmBuf = new StringBuilder();
    for (int i = 0; i < evms.size(); i++) {
      if (i > 0) {
        evmBuf.append(", ");
      }
      evmBuf.append(evms.get(i));
    }

    return String.format("%s [%s,%s] [%s]", getTypeName(), srcDocId, getId(), evmBuf);
  }

  public String toShortString() {
    String srcDocId = getAnnotationBase().getSourceDocument().getId();
    return String.format("%s [%s,%s]", getTypeName(), srcDocId, getId());
  }

  @Override
  public boolean equals(Object obj) {
    if (obj == this) {
      return true;
    }
    // Expect a super class to compare annBase, typeName, and spans.
    if (!super.equals(obj)) {
      return false;
    }
    if (!(obj instanceof Event)) {
      return false;
    }

    Event that = (Event) obj;
    sortEventMentions();
    that.sortEventMentions();
    if (!evms.equals(that.getEventMentions())) {
      return false;
    }

    String thatEventType = that.getEventType();
    if (eventType == null) {
      if (thatEventType != null) {
        return false;
      }
    } else {
      if (!eventType.equals(thatEventType)) {
        return false;
      }
    }

    return true;
  }

  @Override
  public int hashCode() {
    int result = hashCode;
    if (result == 0) {
      result = 17;
      result = 31 * result + evms.hashCode();
      if (eventType != null) {
        result = 31 * result + eventType.hashCode();
      }
      hashCode = result;
    }

    return result;
  }

  /**
   * An element annotation precedes another one if the former's begin precedes the latter's, or the
   * former's end precedes the latter's if the former's begin is equal to the latter's.
   * 
   * @param that
   */
  @Override
  public int compareTo(Event that) {
    sortEventMentions();
    that.sortEventMentions();

    EventMention thisFirstEvm = getEventMentionAt(0);
    EventMention thatFirstEvm = that.getEventMentionAt(0);

    return thisFirstEvm.compareTo(thatFirstEvm);
  }

  public String getEventType() {
    return eventType;
  }

  public void setEventType(String eventType) {
    this.eventType = eventType;
  }

  public EventMention getEventMentionAt(int index) {
    int numEvms = numEventMentions();
    if (index < 0 || index >= numEvms) {
      throw new IndexOutOfBoundsException(String.format("Index: %d, Size: %d", index, numEvms));
    }

    return evms.get(index);
  }

  public List<EventMention> getEventMentions() {
    return evms;
  }

  public boolean hasEventMention(EventMention evm) {
    return evms.contains(evm);
  }

  public void sortEventMentions() {
    Collections.sort(evms);
  }

  public void setEventMentions(List<EventMention> evms) {
    this.evms = evms;
    for (EventMention evm : evms) {
      evm.setEvent(this);
    }
  }

  public void addEventMention(EventMention evm) {
    evms.add(evm);
    evm.setEvent(this);
  }

  public void addEventMentions(List<EventMention> evms) {
    for (EventMention evm : evms) {
      addEventMention(evm);
    }
  }

  public void removeEventMention(EventMention evm) {
    evms.remove(evm);
  }

  public int numEventMentions() {
    return evms.size();
  }

  public boolean isSingleton() {
    return (numEventMentions() == 1);
  }

  public List<EventRelation> getFromEventRelations() {
    return fromRels;
  }

  public void setFromEventRelations(List<EventRelation> fromEventRelations) {
    fromRels = fromEventRelations;
  }

  public void addFromEventRelation(EventRelation fromEventRelation) {
    fromRels.add(fromEventRelation);
  }

  public List<EventRelation> getToEventRelations() {
    return toRels;
  }

  public void setToRels(List<EventRelation> toEventRelations) {
    toRels = toEventRelations;
  }

  public void addToEventRelation(EventRelation toEventRelation) {
    fromRels.add(toEventRelation);
  }

}
