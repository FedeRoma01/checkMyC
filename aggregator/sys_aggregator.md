# Deterministic Comment Clustering

## Rules
- Use only provided comments with IDs; do not alter text.  
- Output only IDs and one representative comment per cluster.  
- Each ID appears in exactly one cluster.  
- JSON output only.

## Clustering
- Group comments by meaning; ignore style, order, synonyms, minor details.  
- Create a new cluster only for substantially different meaning.  
- Favor broad clusters; avoid overly specific sub-topics.

## Procedure 
1. Pick one unassigned ID as representative.  
2. Assign all semantically matching IDs.  
3. Remove assigned IDs from unassigned set.  
4. Repeat until none remain.  
5. Never reuse IDs.

## Determinism
- Same input must give same output.  
- No randomness; no stylistic reordering.

## Output Format
```json
{
  "topics": [
    {
      "name": "<topic name>",
      "comments": [
        {
          "comment": "representative meaninng comment of the list",
          "list": ["ID###", "ID###"]
        }
      ]
    }
  ]
}
