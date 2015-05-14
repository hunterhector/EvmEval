package net.junaraki.annobase.type.element;

import java.util.ArrayList;
import java.util.List;

import net.junaraki.annobase.AnnotationBase;
import net.junaraki.annobase.type.concept.Entity;
import net.junaraki.annobase.type.relation.element.EventArgument;

/**
 * An entity mention annotation.
 * 
 * @author Jun Araki
 */
public class EntityMention extends TokenBasedTextSpan {

  private static final long serialVersionUID = 9160212920331241992L;

  protected String entityType;

  protected Entity entity;

  /** A list of event arguments going to this entity mention */
  protected List<EventArgument> eventArgs;

  /**
   * Public constructor.
   * 
   * @param annBase
   * @param begin
   * @param end
   */
  public EntityMention(AnnotationBase annBase, int begin, int end) {
    super(annBase, begin, end);
    eventArgs = new ArrayList<EventArgument>();
  }

  /**
   * Returns true if an entity mention is equal to the given one in terms of the same annotation
   * base, type name, spans, and entity type.
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
    if (!(obj instanceof EntityMention)) {
      return false;
    }

    EntityMention that = (EntityMention) obj;

    String thatEntityType = that.getEntityType();
    if (entityType == null) {
      if (thatEntityType != null) {
        return false;
      }
    } else {
      if (!entityType.equals(thatEntityType)) {
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
      result = 31 * result + super.hashCode();
      if (entityType != null) {
        result = 31 * result + entityType.hashCode();
      }
      hashCode = result;
    }

    return result;
  }

  @Override
  public String toString() {
    return String.format("%s [%s,%d,%d,%s,%s] [%s]", getTypeName(), getAnnotationBase()
            .getSourceDocument().getId(), getBegin(), getEnd(), getId(), entityType, getText());
  }

  public String getEntityType() {
    return entityType;
  }

  public void setEntityType(String entityType) {
    this.entityType = entityType;
  }

  public Entity getEntity() {
    return entity;
  }

  public void setEntity(Entity entity) {
    this.entity = entity;
  }

  public List<EventArgument> getEventArguments() {
    return eventArgs;
  }

  public void setEventArguments(List<EventArgument> eventArgs) {
    for (EventArgument eventArg : eventArgs) {
      eventArg.setTo(this);
    }
    this.eventArgs = eventArgs;
  }

  /**
   * Adds the given event mention argument to this event mention.
   * 
   * @param eventArg
   */
  public void addEventArgument(EventArgument eventArg) {
    eventArg.setTo(this);
    eventArgs.add(eventArg);
  }

  /**
   * Adds an event mention argument with the given role and elemental annotation to this event
   * mention.
   * 
   * @param role
   * @param fromEvm
   */
  public void addEventArgument(String role, EventMention fromEvm) {
    EventArgument arg = new EventArgument(annBase);
    arg.setRole(role);
    arg.setFrom(fromEvm);
    addEventArgument(arg);
  }

}
