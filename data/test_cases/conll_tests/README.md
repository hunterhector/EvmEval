Test cases for CoNLL tests
==========================
The test works this way, we create two sets of key-response files:

 1. Set 1 (in tbf format):
        - Key file : `TestName.key.tbf`
        - Response file : `TestName_ResponseSuffix.response.tbf`
            There can be multiple response files
 2. Set 2 (in conll format):
        - Key file : `TestName.key.tbf`
        - Response file : `TestName_ResponseSuffix.response.tbf`
            There can be multiple response files

Each different `TestName_ResponseSuffix` will trigger a new
test. We tester will automatically run our scorer on Set 1 and
the original CoNLL scorer on Set 2.

To pass the test, the corresponding (identified by *ResponseSuffix*)
key-response result from Set  1 should match the key-response result
from Set 2.

For example:
`TestA.key.conll vs. TestA_correct.response.conll`
should produce scores identical to
`TestA.key.tbf   vs. TestA_correct.response.tbf`

   
To make this a little bit easier, one can use util/SimpleTbf2Conll.py
to generate CoNLL format from TBF format (and then you can add in 
coreference information manually).