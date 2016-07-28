package net.junaraki.annobase.type.concept;

import java.util.ArrayList;
import java.util.List;

import net.junaraki.annobase.AnnotationBase;
import net.junaraki.annobase.type.AbstractAnnotation;
import net.junaraki.annobase.type.element.EntityMention;

/**
 * This class represents an abstract type of events. Event mentions belonging to an event are
 * coreferential with each other.
 * 
 * @author Jun Araki
 */
public class Entity extends AbstractAnnotation {

  private static final long serialVersionUID = 1406333418736888401L;

  protected String entityType;

  /** A list of entity mentions that belong to this entity, i.e., coreferential entity mentions */
  protected List<EntityMention> enms;

  /**
   * Public constructor.
   * 
   * @param annBase
   */
  public Entity(AnnotationBase annBase) {
    super(annBase);
    enms = new ArrayList<EntityMention>();
  }

  @Override
  public String toString() {
    return String.format("%s [%s]", getTypeName(), getId());
  }

  public String getEntityType() {
    return entityType;
  }

  public void setEntityType(String entityType) {
    this.entityType = entityType;
  }

  public List<EntityMention> getEntityMentions() {
    return enms;
  }

  public void setEntityMentions(List<EntityMention> enms) {
    this.enms = enms;
  }

  public void addEntityMention(EntityMention enm) {
    enms.add(enm);
  }

  public int numEntityMentions() {
    return enms.size();
  }

}
