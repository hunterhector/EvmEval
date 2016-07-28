package net.junaraki.annobase.type.relation.element;

import net.junaraki.annobase.AnnotationBase;

/**
 * This class represents event coreference. Event coreference is an undirected relation to show that
 * two event mentions refer to the same event.
 * 
 * @author Jun Araki
 */
public class EventCoref extends EventMentionRelation {

  private static final long serialVersionUID = -9120195775321503683L;

  /**
   * Public constructor.
   * 
   * @param annBase
   */
  public EventCoref(AnnotationBase annBase) {
    super(annBase);
  }

}
