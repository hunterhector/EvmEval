package converter;

import com.google.common.collect.BiMap;
import com.google.common.collect.HashBiMap;
import net.junaraki.annobase.AnnotationBase;
import net.junaraki.annobase.type.Annotation;
import net.junaraki.annobase.type.concept.Event;
import net.junaraki.annobase.type.element.ElementAnnotation;
import net.junaraki.annobase.type.element.EntityMention;
import net.junaraki.annobase.type.element.EventMention;
import net.junaraki.annobase.type.relation.element.EventArgument;

import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class BratAnnotationBase extends AnnotationBase {

  private static final long serialVersionUID = 3902962276793662013L;

  /** A type of event coreference as a relation in Brat */
  private static final String EVENT_COREF_TYPE = "Coreference";

  /** A type of the first argument of an event coreference link */
  private static final String EVENT_COREF_ARG1_TYPE = "Arg1";

  /** A type of the second argument of an event coreference link */
  private static final String EVENT_COREF_ARG2_TYPE = "Arg2";

  private BiMap<ElementAnnotation, Integer> annToAnnId;

  private int annId, evmId;

  /**
   * Public constructor.
   * 
   * @param text
   */
  public BratAnnotationBase(String text) {
    super(text);
  }

  /**
   * Public constructor.
   * 
   * @param text
   * @param docId
   */
  public BratAnnotationBase(String text, String docId) {
    super(text, docId);
  }

  public void consume(AnnotationBase annBase) {
    if (!srcDoc.equals(annBase.getSourceDocument())) {
      throw new IllegalArgumentException(
              "The given annotation base has a different source document.");
    }

    annMap = annBase.getAnnotationMap();
    for (EntityMention enm : getEntityMentions()) {
      enm.setId(annId); // Entity ID is equal to annotation ID.
      annToAnnId.put(enm, annId);
      annId++;
    }
    for (EventMention evm : getEventMentions()) {
      if (evm.getId() <= 0) {
        evm.setId(evmId);
        evmId++;
      }
      annToAnnId.put(evm, annId);
      annId++;
    }
  }

  @Override
  protected void initialize() {
    super.initialize();
    annToAnnId = HashBiMap.create();
    annId = evmId = 1;
  }

  @Override
  public <T extends Annotation> void addAnnotation(T ann) {
    super.addAnnotation(ann);

    if (ann instanceof EntityMention) {
      EntityMention enm = (EntityMention) ann;
      enm.setId(annId); // Entity ID is equal to annotation ID.
      annToAnnId.put(enm, annId);
      annId++;
    } else if (ann instanceof EventMention) {
      EventMention evm = (EventMention) ann;
      if (evm.getId() <= 0) {
        evm.setId(evmId);
        evmId++;
      }
      annToAnnId.put(evm, annId);
      annId++;
    }
  }

  /**
   * Returns true if there is an event mention whose ID is the given one.
   * 
   * @param evmId
   * @return
   */
  public boolean hasEventMention(int evmId) {
    for (EventMention evm : getEventMentions()) {
      if (evmId == evm.getId()) {
        return true;
      }
    }

    return false;
  }

  public int getAnnotationId(ElementAnnotation ann) {
    if (annToAnnId.containsKey(ann)) {
      return annToAnnId.get(ann);
    }
    return -1;
  }

  public ElementAnnotation getAnnotation(int annId) {
    if (annToAnnId.inverse().containsKey(annId)) {
      annToAnnId.inverse().get(annId);
    }
    return null;
  }

  @Override
  public String toString() {
    // Initialization
    int relId = 1;

    StringBuilder buf = new StringBuilder();

    for (EntityMention enm : getEntityMentions()) {
      int annId = annToAnnId.get(enm);
      buf.append(BratFormatter.formatEntityMention(annId, enm));
      buf.append(System.lineSeparator());
    }

    for (EventMention evm : getEventMentions()) {
      int evmAnnId = annToAnnId.get(evm);

      Map<String, Integer> argToAnnId = new HashMap<String, Integer>();
      for (EventArgument arg : evm.getEventArguments()) {
        EntityMention enm = arg.getTo();
        if (!annToAnnId.containsKey(enm)) {
          throw new RuntimeException("Unexpected error: annotation ID is not found.");
        }

        int enmAnnId = annToAnnId.get(enm);
        argToAnnId.put(arg.getRole(), enmAnnId);
      }

      // Use annotation ID for attribute ID
      buf.append(BratFormatter.formatEventMention(evmAnnId, evmAnnId, evm, argToAnnId));
      buf.append(System.lineSeparator());
    }

    // Event coreference link annotations; annotate links from a cluster
    for (Event event : getEvents()) {
      List<EventMention> evms = event.getEventMentions();
      Collections.sort(evms);
      for (int i = 0; i < evms.size() - 1; i++) {
        EventMention evm1 = evms.get(i);
        EventMention evm2 = evms.get(i + 1);
        int evmId1 = evm1.getId();
        int evmId2 = evm2.getId();

        buf.append(BratFormatter.formatEventRelation(relId, EVENT_COREF_TYPE,
                EVENT_COREF_ARG1_TYPE, evmId1, EVENT_COREF_ARG2_TYPE, evmId2));
        buf.append(System.lineSeparator());

        relId++;
      }
    }

    return buf.toString();
  }

}
