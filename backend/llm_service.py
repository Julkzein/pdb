"""
LLM Service for enhancing orchestrations with DeepSeek AI
Provides contextual teaching resources and suggestions at 50-100x lower cost!
"""

import os
import json
from openai import OpenAI
from typing import Dict, Any, Optional


class LLMService:
    """Service for interacting with DeepSeek API to enhance orchestrations"""

    def __init__(self):
        """Initialize the DeepSeek client"""
        self.api_key = os.getenv('DEEPSEEK_API_KEY')
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY environment variable not set")

        # DeepSeek uses OpenAI-compatible API
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com"
        )

        # DeepSeek's latest model (much cheaper than Claude!)
        self.model = "deepseek-chat"

    def enhance_orchestration(
        self,
        orchestration: Dict[str, Any],
        age_group: str,
        subject: str
    ) -> Dict[str, Any]:
        """
        Enhance an orchestration with contextual teaching resources

        Args:
            orchestration: The orchestration graph state
            age_group: Age group of students (e.g., "12-13 years old")
            subject: Subject being taught (e.g., "Photosynthesis")

        Returns:
            Dictionary with enhancement data structured for frontend display
        """

        # Construct the prompt
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(orchestration, age_group, subject)

        try:
            # Call DeepSeek API (OpenAI-compatible)
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=4096,
                response_format={"type": "json_object"}  # Force JSON output
            )

            # Parse the response
            content = response.choices[0].message.content

            # Parse JSON from response (should be clean JSON due to response_format)
            enhancement_data = json.loads(content)

            # Add metadata
            result = {
                "enhancements": enhancement_data,
                "metadata": {
                    "model": self.model,
                    "provider": "DeepSeek",
                    "ageGroup": age_group,
                    "subject": subject,
                    "inputTokens": response.usage.prompt_tokens,
                    "outputTokens": response.usage.completion_tokens,
                    "totalTokens": response.usage.total_tokens
                }
            }

            return result

        except Exception as e:
            raise Exception(f"Failed to enhance orchestration: {str(e)}")

    def _build_system_prompt(self) -> str:
        """Build the system prompt for DeepSeek"""
        return """You are an expert educational consultant helping teachers adapt lesson plans for specific age groups and subjects.

Your role is to:
1. Provide concrete, actionable teaching resources and examples
2. Suggest age-appropriate adaptations for pedagogical activities
3. Recommend specific resources (videos, tools, worksheets) when possible
4. Offer practical teaching tips for the specific subject and age group

You receive an orchestration (sequence of learning activities) and provide contextual enhancements that help teachers implement it effectively.

IMPORTANT: Return your response as valid JSON only. Use the exact structure specified in the user prompt."""

    def _build_user_prompt(
        self,
        orchestration: Dict[str, Any],
        age_group: str,
        subject: str
    ) -> str:
        """Build the user prompt with orchestration details"""

        # Plane mapping
        PLANE_NAMES = {0: "Individual", 1: "Team", 2: "Class"}

        # Extract key information
        activities = orchestration.get('activities', [])
        total_time = orchestration.get('totTime', 0)
        goal = orchestration.get('goal', {})
        start = orchestration.get('start', {})

        # Build activity list
        activity_list = []
        for idx, act in enumerate(activities):
            plane_name = PLANE_NAMES.get(act.get('plane', 0), "Unknown")
            description = act.get('activityDescription', act.get('description', 'No description'))
            activity_list.append(
                f"{idx + 1}. {act['activityName']} ({act['time']} min) - {plane_name} work - {description}"
            )

        activities_text = "\n".join(activity_list) if activity_list else "No activities yet"

        # Format p-values
        goal_pvalue = f"Fluency: {goal.get('v', [0, 0])[0]:.2f}, Depth: {goal.get('v', [0, 0])[1]:.2f}"
        start_pvalue = f"Fluency: {start.get('v', [0, 0])[0]:.2f}, Depth: {start.get('v', [0, 0])[1]:.2f}"

        prompt = f"""I have created a lesson orchestration with the following details:

CONTEXT:
- Age Group: {age_group}
- Subject: {subject}
- Total Duration: {total_time} minutes
- Starting Point: {start_pvalue}
- Learning Goal: {goal_pvalue}

ACTIVITY SEQUENCE:
{activities_text}

Please provide enhancements for this orchestration in JSON format with the following exact structure:

{{
  "overallSuggestions": {{
    "ageAdaptations": "How to adapt the overall lesson for this age group",
    "subjectContext": "Key considerations for teaching this specific subject",
    "estimatedDifficulty": "easy|moderate|challenging"
  }},
  "activityEnhancements": [
    {{
      "activityPosition": 0,
      "activityName": "Activity name",
      "concreteExample": "A specific, detailed example of how to implement this activity for {subject} with {age_group} students",
      "resources": [
        {{"type": "video", "title": "Resource name", "description": "Brief description", "suggestedUrl": "URL if you know a real one, or general search terms"}},
        {{"type": "worksheet", "title": "Another resource", "description": "What it provides", "suggestedUrl": "search terms"}}
      ],
      "teachingTips": "Practical tips for implementing this specific activity with this age group and subject",
      "timeManagement": "Advice on pacing this activity for the given age group"
    }}
  ],
  "additionalResources": [
    {{"type": "reference", "title": "Resource name", "description": "What it provides", "suggestedUrl": "URL or search terms"}}
  ]
}}

Guidelines:
- Provide one activityEnhancement entry for EACH activity in the sequence (positions 0 through {len(activities)-1})
- For resources, types can be: video, worksheet, tool, simulation, article, reference, community
- Prioritize: concrete examples, specific teaching tips, and resource recommendations
- Make it practical and immediately usable for a teacher

Return ONLY the JSON object, no other text."""

        return prompt

    def _parse_json_response(self, content: str) -> Dict[str, Any]:
        """Parse JSON from Claude's response, handling markdown code blocks"""

        # Try to extract JSON from markdown code blocks
        if "```json" in content:
            start = content.find("```json") + 7
            end = content.find("```", start)
            content = content[start:end].strip()
        elif "```" in content:
            start = content.find("```") + 3
            end = content.find("```", start)
            content = content[start:end].strip()

        # Parse JSON
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            # Fallback: try to find JSON object in the response
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            raise ValueError(f"Could not parse JSON from response: {e}")


def create_llm_service() -> Optional[LLMService]:
    """
    Create an LLM service instance if API key is available
    Returns None if API key is not configured
    """
    try:
        return LLMService()
    except ValueError:
        # API key not configured - graceful degradation
        return None
