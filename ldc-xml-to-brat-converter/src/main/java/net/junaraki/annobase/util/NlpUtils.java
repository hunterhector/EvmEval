package net.junaraki.annobase.util;

import java.util.Arrays;
import java.util.List;

import net.junaraki.annobase.type.element.DependencyNode;
import net.junaraki.annobase.type.element.Token;
import net.junaraki.annobase.type.relation.element.DependencyRelation;
import net.junaraki.annobase.util.NlpConstants.PartOfSpeechTag;

/**
 * This class provides various utility methods for natural language process in general.
 * 
 * @author Jun Araki
 */
public class NlpUtils {

  /**
   * Returns the determiner of the given token, if any.
   * 
   * @param token
   * @return
   */
  public static Token getDeterminer(Token token) {
    DependencyNode depNode = token.getDependencyNode();
    if (depNode == null) {
      return null;
    }

    for (DependencyRelation childRel : depNode.getChildRelations()) {
      Token childToken = childRel.getChild().getToken();
      String childRelType = childRel.getDependencyType();
      if ("det".equals(childRelType)) {
        // Found a determiner.
        return childToken;
      }
    }

    return null;
  }

  /**
   * Returns a list of definite determiners.
   * 
   * @return
   */
  public static List<String> getDefiniteDeterminers() {
    return Arrays.asList("the", "this", "that", "these", "those", "my", "your", "his", "her",
            "its", "our", "their", "whose", "which", "what");
  }

  /**
   * Returns true if the part-of-speech tag given in the first argument represents the
   * part-of-speech given in the second argument.
   * 
   * @param posTag
   * @param pos
   * @return
   */
  private static boolean isParticularPos(String posTag, PartOfSpeechTag pos) {
    if (posTag == null || posTag.equals("")) {
      return false;
    }

    if (posTag.equals(pos.toString())) {
      return true;
    }

    return false;
  }

  /**
   * Returns true if the given part-of-speech tag is a determiner.
   * 
   * @param input
   * @return true if the specified string is the basic determiner; false otherwise.
   */
  public static boolean isDeterminer(Token token) {
    return isDeterminer(token.getPos());
  }

  public static boolean isDeterminer(String posTag) {
    return isParticularPos(posTag, PartOfSpeechTag.DT);
  }

  public static boolean isCommonNoun(Token token) {
    return isCommonNoun(token.getPos());
  }

  public static boolean isCommonNoun(String posTag) {
    return (isSingularNonProperNoun(posTag) || isPluralNonProperNoun(posTag));
  }

  public static boolean isProperNoun(Token token) {
    return isProperNoun(token.getPos());
  }

  public static boolean isProperNoun(String posTag) {
    return (isSingularProperNoun(posTag) || isPluralProperNoun(posTag));
  }

  public static boolean isPronoun(Token token) {
    return isPronoun(token.getPos());
  }

  public static boolean isPronoun(String posTag) {
    return (isPersonalPronoun(posTag) || isPossessivePronoun(posTag));
  }

  public static boolean isPersonalPronoun(Token token) {
    return isPersonalPronoun(token.getPos());
  }

  public static boolean isPersonalPronoun(String posTag) {
    return isParticularPos(posTag, PartOfSpeechTag.PRP);
  }

  public static boolean isPossessivePronoun(Token token) {
    return isPossessivePronoun(token.getPos());
  }

  public static boolean isPossessivePronoun(String posTag) {
    return isParticularPos(posTag, PartOfSpeechTag.PRP$);
  }

  public static boolean isSingularNonProperNoun(Token token) {
    return isSingularNonProperNoun(token.getPos());
  }

  public static boolean isSingularNonProperNoun(String posTag) {
    return isParticularPos(posTag, PartOfSpeechTag.NN);
  }

  public static boolean isSingularProperNoun(Token token) {
    return isSingularProperNoun(token.getPos());
  }

  public static boolean isSingularProperNoun(String posTag) {
    return isParticularPos(posTag, PartOfSpeechTag.NNP);
  }

  public static boolean isSingularNoun(Token token) {
    return isSingularNoun(token.getPos());
  }

  public static boolean isSingularNoun(String posTag) {
    return (isSingularNonProperNoun(posTag) || isSingularProperNoun(posTag));
  }

  public static boolean isPluralNonProperNoun(Token token) {
    return isPluralNonProperNoun(token.getPos());
  }

  public static boolean isPluralNonProperNoun(String posTag) {
    return isParticularPos(posTag, PartOfSpeechTag.NNS);
  }

  public static boolean isPluralProperNoun(Token token) {
    return isPluralProperNoun(token.getPos());
  }

  public static boolean isPluralProperNoun(String posTag) {
    return isParticularPos(posTag, PartOfSpeechTag.NNPS);
  }

  public static boolean isPluralNoun(Token token) {
    return isPluralNoun(token.getPos());
  }

  public static boolean isPluralNoun(String posTag) {
    return (isPluralNonProperNoun(posTag) || isPluralProperNoun(posTag));
  }

  public static boolean isNoun(Token token) {
    return isNoun(token.getPos());
  }

  public static boolean isNoun(String posTag) {
    return (isCommonNoun(posTag) || isProperNoun(posTag) || isPronoun(posTag));
  }

  public static boolean isVerb(Token token) {
    return isVerb(token.getPos());
  }

  public static boolean isVerb(String posTag) {
    return (isBaseFormVerb(posTag) || isPresentVerb(posTag) || isPastVerb(posTag)
            || isPastParticipleVerb(posTag) || isGerund(posTag));
  }

  public static boolean isBaseFormVerb(Token token) {
    return isBaseFormVerb(token.getPos());
  }

  public static boolean isBaseFormVerb(String posTag) {
    return isParticularPos(posTag, PartOfSpeechTag.VB);
  }

  public static boolean isPresentVerb(Token token) {
    return isPresentVerb(token.getPos());
  }

  public static boolean isPresentVerb(String posTag) {
    return (isNon3rdPersonPresentVerb(posTag) || is3rdPersonPresentVerb(posTag));
  }

  public static boolean isNon3rdPersonPresentVerb(Token token) {
    return isNon3rdPersonPresentVerb(token.getPos());
  }

  public static boolean isNon3rdPersonPresentVerb(String posTag) {
    return isParticularPos(posTag, PartOfSpeechTag.VBP);
  }

  public static boolean is3rdPersonPresentVerb(Token token) {
    return is3rdPersonPresentVerb(token.getPos());
  }

  public static boolean is3rdPersonPresentVerb(String posTag) {
    return isParticularPos(posTag, PartOfSpeechTag.VBZ);
  }

  public static boolean isPastVerb(Token token) {
    return isPastVerb(token.getPos());
  }

  public static boolean isPastVerb(String posTag) {
    return isParticularPos(posTag, PartOfSpeechTag.VBD);
  }

  public static boolean isPastParticipleVerb(Token token) {
    return isPastParticipleVerb(token.getPos());
  }

  public static boolean isPastParticipleVerb(String posTag) {
    return isParticularPos(posTag, PartOfSpeechTag.VBN);
  }

  public static boolean isGerund(Token token) {
    return isGerund(token.getPos());
  }

  public static boolean isGerund(String posTag) {
    return isParticularPos(posTag, PartOfSpeechTag.VBG);
  }

  public static boolean isAdjective(Token token) {
    return isAdjective(token.getPos());
  }

  public static boolean isAdjective(String posTag) {
    if (posTag.startsWith(PartOfSpeechTag.JJ.toString())) {
      return true;
    }

    return false;
  }

  public static boolean isAdverb(Token token) {
    return isAdverb(token.getPos());
  }

  public static boolean isAdverb(String posTag) {
    if (posTag.startsWith(PartOfSpeechTag.RB.toString())) {
      return true;
    }

    return false;
  }

  public static boolean isWhDeterminer(Token token) {
    return isWhDeterminer(token.getPos());
  }

  public static boolean isWhDeterminer(String posTag) {
    return isParticularPos(posTag, PartOfSpeechTag.WDT);
  }

  public static boolean isWhPronoun(Token token) {
    return isWhPronoun(token.getPos());
  }

  public static boolean isWhPronoun(String posTag) {
    return isParticularPos(posTag, PartOfSpeechTag.WP);
  }

  public static boolean isWhPossessivePronoun(Token token) {
    return isWhPossessivePronoun(token.getPos());
  }

  public static boolean isWhPossessivePronoun(String posTag) {
    return isParticularPos(posTag, PartOfSpeechTag.WP$);
  }

  public static boolean isWhAdverb(Token token) {
    return isWhAdverb(token.getPos());
  }

  public static boolean isWhAdverb(String posTag) {
    return isParticularPos(posTag, PartOfSpeechTag.WRB);
  }

  public static boolean isPrepositionOrSubordinatingConjunction(Token token) {
    return isPrepositionOrSubordinatingConjunction(token.getPos());
  }

  public static boolean isPrepositionOrSubordinatingConjunction(String posTag) {
    return isParticularPos(posTag, PartOfSpeechTag.IN);
  }

  public static boolean isCoordinatingConjunction(Token token) {
    return isCoordinatingConjunction(token.getPos());
  }

  public static boolean isCoordinatingConjunction(String posTag) {
    return isParticularPos(posTag, PartOfSpeechTag.CC);
  }

  public static boolean isCardinalNumber(Token token) {
    return isCardinalNumber(token.getPos());
  }

  public static boolean isCardinalNumber(String posTag) {
    return isParticularPos(posTag, PartOfSpeechTag.CD);
  }

  public static boolean isParticle(Token token) {
    return isParticle(token.getPos());
  }

  public static boolean isParticle(String posTag) {
    return isParticularPos(posTag, PartOfSpeechTag.RP);
  }

}
