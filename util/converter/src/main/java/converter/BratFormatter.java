package converter;

import java.util.List;
import java.util.Map;

import org.apache.commons.lang3.StringUtils;

import com.google.common.base.Joiner;
import com.google.common.base.Splitter;

import net.junaraki.annobase.type.element.ElementAnnotation;
import net.junaraki.annobase.type.element.EntityMention;
import net.junaraki.annobase.type.element.EventMention;
import net.junaraki.annobase.type.element.Token;

/**
 * This class provides various utilities to deal with annotations along with Brat's standoff format.
 * 
 * @see http://brat.nlplab.org/standoff.html
 * @author Jun Araki
 */
public class BratFormatter {

  private static Splitter newlineSplitter;

  private static Joiner whitespaceJoiner;

  static {
    newlineSplitter = Splitter.on("\n");
    whitespaceJoiner = Joiner.on(" ");
  }

  /**
   * Returns a one-line text-bound annotation from the given specification.
   * 
   * @param annId
   * @param type
   * @param ann
   * @return
   */
  public static String formatTextBoundAnnotation(int annId, String type, ElementAnnotation ann) {
    StringBuilder buf = new StringBuilder();

    int begin = ann.getBegin();
    int end = ann.getEnd();
    String text = ann.getText();

    buf.append("T");
    buf.append(annId);
    buf.append("\t");
    buf.append(type);
    buf.append(" ");
    if (!text.contains("\n")) {
      buf.append(begin);
      buf.append(" ");
      buf.append(end);
      buf.append("\t");
      buf.append(text);
    } else {
      List<String> subtexts = newlineSplitter.splitToList(text);
      for (int i = 0; i < subtexts.size(); i++) {
        if (i > 0) {
          buf.append(";");
        }
        String subtext = subtexts.get(i);

        end = begin + subtext.length();
        buf.append(begin);
        buf.append(" ");
        buf.append(end);

        begin = end + 1;
      }
      buf.append("\t");
      buf.append(whitespaceJoiner.join(subtexts));
    }

    return buf.toString();
  }

  /**
   * Returns a token annotation in the Brat format.
   * 
   * @param annId
   * @param token
   * @return
   */
  public static String formatToken(int annId, Token token) {
    String pos = token.getPos();
    if ("PRP$".equals(pos)) {
      pos = "PossessivePronoun";
    } else if ("WP$".equals(pos)) {
      pos = "PossessiveWhPronoun";
    } else if (",".equals(pos)) {
      pos = "Comma";
    } else if (".".equals(pos)) {
      pos = "Period";
    } else if (":".equals(pos)) {
      pos = "Colon";
    } else if ("``".equals(pos)) {
      pos = "DoubleQutationBegin";
    } else if ("''".equals(pos)) {
      pos = "DoubleQutationEnd";
    }

    return formatTextBoundAnnotation(annId, pos, token);
  }

  /**
   * Returns an entity mention annotation in the Brat format.
   * 
   * @param entityId
   * @param entityType
   * @param begin
   * @param end
   * @param text
   * @return
   */
  public static String formatEntityMention(int annId, EntityMention enm) {
    return formatTextBoundAnnotation(annId, enm.getEntityType(), enm);
  }

  /**
   * Returns a one-line event mention annotation from the given specification. This does not include
   * a text-bound annotation for an event.
   * 
   * @param annId
   * @param eventId
   * @param eventType
   * @param argToAnnId
   * @return
   */
  public static String formatEventMention(int annId, int eventId, String eventType,
          Map<String, Integer> argToAnnId) {
    StringBuilder buf = new StringBuilder();

    buf.append("E");
    buf.append(eventId);
    buf.append("\t");
    buf.append(eventType);
    buf.append(":");
    buf.append("T");
    buf.append(annId);
    for (String arg : argToAnnId.keySet()) {
      int argAnnId = argToAnnId.get(arg);
      buf.append(" ");
      buf.append(arg);
      buf.append(":");
      buf.append("T");
      buf.append(argAnnId);
    }

    return buf.toString();
  }

  /**
   * Returns a one-line event attribute annotation from the given specification.
   * 
   * @param eventId
   * @param attrId
   * @param epistemicStatus
   * @return
   */
  public static String formatEventAttribute(int eventId, int attrId, String epistemicStatus) {
    StringBuilder buf = new StringBuilder();

    buf.append("A");
    buf.append(attrId);
    buf.append("\t");
    buf.append("Realis");
    buf.append(" ");
    buf.append("E");
    buf.append(eventId);
    buf.append(" ");
    buf.append(epistemicStatus);

    return buf.toString();
  }

  /**
   * Returns a two-line event mention annotation from the given specification.
   * 
   * @param annId
   * @param eventId
   * @param attrId
   * @param evm
   * @param argToAnnId
   * @return
   */
  public static String formatEventMention(int annId, int attrId, EventMention evm,
          Map<String, Integer> argToAnnId) {
    StringBuilder buf = new StringBuilder();

    String eventType = evm.getEventType();
    String epistemicStatus = evm.getEpistemicStatus();

    buf.append(formatTextBoundAnnotation(annId, eventType, evm));
    buf.append(System.lineSeparator());
    buf.append(formatEventMention(annId, evm.getId(), eventType, argToAnnId));
    if (StringUtils.isNotEmpty(epistemicStatus)) {
      buf.append(System.lineSeparator());
      buf.append(formatEventAttribute(evm.getId(), attrId, epistemicStatus));
    }

    return buf.toString();
  }

  /**
   * Returns a one-line entity-entity relation annotation from the given specification.
   * 
   * @param relId
   * @param relType
   * @param argType1
   * @param annId1
   * @param argType2
   * @param annId2
   * @return
   */
  public static String formatEntityRelation(int relId, String relType, String argType1, int annId1,
          String argType2, int annId2) {
    StringBuilder buf = new StringBuilder();

    buf.append("R");
    buf.append(relId);
    buf.append("\t");
    buf.append(relType);
    buf.append(" ");
    buf.append(argType1);
    buf.append(":");
    buf.append("T");
    buf.append(annId1);
    buf.append(" ");
    buf.append(argType2);
    buf.append(":");
    buf.append("T");
    buf.append(annId2);

    return buf.toString();
  }

  /**
   * Returns a one-line event-event relation annotation from the given specification.
   * 
   * @param relId
   * @param relType
   * @param argType1
   * @param evmId1
   * @param argType2
   * @param evmId2
   * @return
   */
  public static String formatEventRelation(int relId, String relType, String argType1, int evmId1,
          String argType2, int evmId2) {
    StringBuilder buf = new StringBuilder();

    buf.append("R");
    buf.append(relId);
    buf.append("\t");
    buf.append(relType);
    buf.append(" ");
    buf.append(argType1);
    buf.append(":");
    buf.append("E");
    buf.append(evmId1);
    buf.append(" ");
    buf.append(argType2);
    buf.append(":");
    buf.append("E");
    buf.append(evmId2);

    return buf.toString();
  }

}
