package net.junaraki.annobase.type.element;

import java.util.ArrayList;
import java.util.List;

import net.junaraki.annobase.AnnotationBase;
import net.junaraki.annobase.type.concept.Event;
import net.junaraki.annobase.type.relation.element.EventArgument;
import net.junaraki.annobase.type.relation.element.EventCoref;
import net.junaraki.annobase.type.relation.element.EventMentionRelation;
import net.junaraki.annobase.type.relation.element.Subevent;

/**
 * An event mention annotation.
 * 
 * @author Jun Araki
 */
public class EventMention extends TokenBasedTextSpan {

  private static final long serialVersionUID = 2166084144014660043L;

  protected String eventType;

  protected String epistemicStatus;

  protected Event event;

  /** A list of event arguments coming from this event mention */
  protected List<EventArgument> eventArgs;

  protected List<EventMentionRelation> fromRels;

  protected List<EventMentionRelation> toRels;

  /**
   * Public constructor.
   * 
   * @param annBase
   * @param begin
   * @param end
   */
  public EventMention(AnnotationBase annBase, int begin, int end) {
    super(annBase, begin, end);
    eventArgs = new ArrayList<EventArgument>();
    fromRels = new ArrayList<EventMentionRelation>();
    toRels = new ArrayList<EventMentionRelation>();
  }

  @Override
  public String toString() {
    String srcDocId = getAnnotationBase().getSourceDocument().getId();
    return String.format("%s [%s,%d,%d,%s,%s] [%s]", getTypeName(), srcDocId, getBegin(), getEnd(),
            getId(), eventType, getText());
  }

  /**
   * Returns true if an event mention is equal to the given one in terms of the same annotation
   * base, type name, spans, and event type.
   */
  @Override
  public boolean equals(Object obj) {
    if (obj == this) {
      return true;
    }
    // Expect a super class to compare annBase, typeName, and spans.
    if (!super.equals(obj)) {
      return false;
    }
    if (!(obj instanceof EventMention)) {
      return false;
    }

    EventMention that = (EventMention) obj;

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

    // For now, ignore epistemic status.
    // String thatEpistemicStatus = that.getEpistemicStatus();
    // if (epistemicStatus == null) {
    // if (thatEpistemicStatus != null) {
    // return false;
    // }
    // } else {
    // if (!epistemicStatus.equals(thatEpistemicStatus)) {
    // return false;
    // }
    // }

    return true;
  }

  @Override
  public int hashCode() {
    int result = hashCode;
    if (result == 0) {
      result = 17;
      result = 31 * result + super.hashCode();
      if (eventType != null) {
        result = 31 * result + eventType.hashCode();
      }
      if (epistemicStatus != null) {
        result = 31 * result + epistemicStatus.hashCode();
      }
      hashCode = result;
    }

    return result;
  }

  public String getEventType() {
    return eventType;
  }

  public void setEventType(String eventType) {
    this.eventType = eventType;
  }

  public String getEpistemicStatus() {
    return epistemicStatus;
  }

  public void setEpistemicStatus(String epistemicStatus) {
    this.epistemicStatus = epistemicStatus;
  }

  public Event getEvent() {
    return event;
  }

  public void setEvent(Event event) {
    this.event = event;
  }

  public List<EventArgument> getEventArguments() {
    return eventArgs;
  }

  public void setEventArguments(List<EventArgument> eventArgs) {
    for (EventArgument eventArg : eventArgs) {
      eventArg.setFrom(this);
    }
    this.eventArgs = eventArgs;
  }

  /**
   * Adds the given event argument to this event mention.
   * 
   * @param eventArg
   */
  public void addEventArgument(EventArgument eventArg) {
    eventArg.setFrom(this);
    eventArgs.add(eventArg);
  }

  /**
   * Removes the given event argument from this event mention.
   * 
   * @param eventArg
   */
  public void removeEventArgument(EventArgument eventArg) {
    eventArg.setFrom(null);
    eventArgs.remove(eventArg);
  }

  /**
   * Adds an event mention argument with the given role and elemental annotation to this event
   * mention.
   * 
   * @param role
   * @param toAnn
   */
  public void addEventArgument(String role, ElementAnnotation toAnn) {
    EventArgument arg = new EventArgument(annBase);
    arg.setRole(role);
    arg.setTo(toAnn);
    addEventArgument(arg);
  }

  public int numEventArguments() {
    return eventArgs.size();
  }

  public List<EventMentionRelation> getFromEventMentionRelations() {
    return fromRels;
  }

  public void setFromEventMentionRelations(List<EventMentionRelation> fromRels) {
    this.fromRels = fromRels;
  }

  public void addFromEventMentionRelation(EventMentionRelation fromRel) {
    fromRels.add(fromRel);
  }

  public void addFromEventMentionRelations(List<EventMentionRelation> fromRels) {
    this.fromRels.addAll(fromRels);
  }

  public List<EventMentionRelation> getToEventMentionRelations() {
    return toRels;
  }

  public void setToEventMentionRelations(List<EventMentionRelation> toRels) {
    this.toRels = toRels;
  }

  public void addToEventMentionRelation(EventMentionRelation toRel) {
    toRels.add(toRel);
  }

  public void addToEventMentionRelations(List<EventMentionRelation> toRels) {
    this.toRels.addAll(toRels);
  }

  /**
   * Returns true if this event mention corefers to the given event mention.
   * 
   * @param evm
   * @return
   */
  public boolean isCoref(EventMention evm) {
    // Check based on links
    for (EventMentionRelation fromRel : fromRels) {
      if (fromRel instanceof EventCoref) {
        if (fromRel.getFrom().equals(this) && fromRel.getTo().equals(evm)) {
          return true;
        }
      }
    }
    for (EventMentionRelation toRel : toRels) {
      if (toRel instanceof EventCoref) {
        if (toRel.getFrom().equals(evm) && toRel.getTo().equals(this)) {
          return true;
        }
      }
    }
    // Check based on clusters
    if (event != null && event.getEventMentions().contains(evm)) {
      return true;
    }

    return false;
  }

  /**
   * Returns true if this event mention is a subevent of the given event mention.
   * 
   * @param evm
   * @return
   */
  public boolean isSubevent(EventMention evm) {
    for (EventMentionRelation toRel : toRels) {
      if (toRel instanceof Subevent) {
        if (toRel.getFrom().equals(evm) && toRel.getTo().equals(this)) {
          return true;
        }
      }
    }
    return false;
  }

}
