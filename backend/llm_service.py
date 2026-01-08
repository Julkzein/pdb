"""
LLM Service for enhancing orchestrations with DeepSeek AI
Provides contextual teaching resources and suggestions at 50-100x lower cost!
"""

import os
import json
import time
from openai import OpenAI, Timeout
from typing import Dict, Any, Optional
import httpx


class LLMService:
    """Service for interacting with DeepSeek API to enhance orchestrations"""

    def __init__(self, library=None):
        """Initialize the DeepSeek client"""
        self.api_key = os.getenv('DEEPSEEK_API_KEY')
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY environment variable not set")

        # DeepSeek uses OpenAI-compatible API with increased timeouts
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com",
            timeout=Timeout(
                connect=30.0,   # 30s to establish connection (5s default)
                read=600.0,     # 10 minutes to read response
                write=60.0,     # 1 minute to send request
                pool=60.0       # 1 minute for connection pooling
            ),
            max_retries=2  # Retry failed requests twice
        )

        # DeepSeek's latest model 
        self.model = "deepseek-chat"

        # Store library reference for activity-specific prompts
        self.library = library

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

        # Track timing for diagnostics
        start_time = time.time()
        connect_time = None
        response_time = None

        try:
            print(f"\n[LLM] Starting DeepSeek API call...")
            print(f"[LLM] Activities: {len(orchestration.get('activities', []))}")
            print(f"[LLM] Prompt size: ~{(len(system_prompt) + len(user_prompt)) // 4} tokens")

            # Call DeepSeek API (OpenAI-compatible)
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,  # Lower temperature for faster, more deterministic responses (to tweak if necessary)
                max_tokens=3000,
                response_format={"type": "json_object"}  # Force JSON output
            )

            response_time = time.time() - start_time
            print(f"[LLM] [SUCCESS] Response received in {response_time:.2f}s")

            # Parse the response
            content = response.choices[0].message.content

            # Parse JSON from response 
            enhancement_data = json.loads(content)

            total_time = time.time() - start_time
            print(f"[LLM] [SUCCESS] Total processing time: {total_time:.2f}s")
            print(f"[LLM] Tokens - Input: {response.usage.prompt_tokens}, Output: {response.usage.completion_tokens}")

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
                    "totalTokens": response.usage.total_tokens,
                    "responseTime": round(response_time, 2),
                    "totalTime": round(total_time, 2)
                }
            }

            return result

        except httpx.ConnectTimeout as e:
            elapsed = time.time() - start_time
            error_msg = f"Connection timeout after {elapsed:.1f}s - DeepSeek API took too long to connect. This may be due to network issues or API load. Please try again."
            print(f"[LLM] [FAILED] CONNECTION TIMEOUT: {error_msg}")
            raise Exception(error_msg)

        except httpx.ReadTimeout as e:
            elapsed = time.time() - start_time
            error_msg = f"Read timeout after {elapsed:.1f}s - DeepSeek API connected but took too long to respond. Try reducing the number of activities or simplifying the request."
            print(f"[LLM] [FAILED] READ TIMEOUT: {error_msg}")
            raise Exception(error_msg)

        except httpx.HTTPStatusError as e:
            error_msg = f"DeepSeek API error (HTTP {e.response.status_code}): {e.response.text}"
            print(f"[LLM] [FAILED] HTTP ERROR: {error_msg}")
            raise Exception(error_msg)

        except json.JSONDecodeError as e:
            error_msg = f"Failed to parse DeepSeek response as JSON: {str(e)}"
            print(f"[LLM] [FAILED] JSON PARSE ERROR: {error_msg}")
            raise Exception(error_msg)

        except Exception as e:
            elapsed = time.time() - start_time
            error_msg = f"Failed to enhance orchestration after {elapsed:.1f}s: {str(e)}"
            print(f"[LLM] [FAILED] GENERAL ERROR: {error_msg}")
            raise Exception(error_msg)

    def _build_system_prompt(self) -> str:
        """Build the system prompt for DeepSeek"""
        return """You are an expert educational consultant helping teachers adapt lesson plans for specific age groups and subjects.

Your role is to:
1. GENERATE ACTUAL READY-TO-USE CONTENT - not descriptions of what to create
2. When asked for slides, write the actual slide content with titles and bullet points
3. When asked for exercises, write the actual exercise questions with answers
4. When asked for flashcards, write the actual flashcard questions and answers
5. When asked for a challenge, write the actual challenge problem statement
6. Be EXPLICIT and LITERAL - provide the exact content a teacher can copy and use immediately

You receive an orchestration (sequence of learning activities) and provide contextual enhancements that help teachers implement it effectively.

CRITICAL: Your "concreteExample" field must contain the ACTUAL CONTENT requested (slides, exercises, worksheets, etc.), NOT a description of how to create it. Teachers should be able to copy-paste your output directly into their lesson.

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

        # Build activity list with custom prompts
        activity_list = []
        activity_custom_prompts = {}

        for idx, act in enumerate(activities):
            plane_name = PLANE_NAMES.get(act.get('plane', 0), "Unknown")
            description = act.get('activityDescription', act.get('description', 'No description'))
            activity_list.append(
                f"{idx + 1}. {act['activityName']} ({act['time']} min) - {plane_name} work - {description}"
            )

            # Get activity-specific prompt from library if available
            if self.library:
                activity_idx = act.get('activityIdx')
                if activity_idx is not None:
                    activity_data = self.library.getActData(activity_idx)
                    if activity_data and activity_data.llm_prompt:
                        # Substitute placeholders in the custom prompt
                        custom_prompt = activity_data.llm_prompt
                        custom_prompt = custom_prompt.replace('<task>', subject)
                        custom_prompt = custom_prompt.replace('<subject>', subject)
                        custom_prompt = custom_prompt.replace('<age>', str(age_group))
                        custom_prompt = custom_prompt.replace('<duration>', str(act['time']))
                        activity_custom_prompts[idx] = custom_prompt

        activities_text = "\n".join(activity_list) if activity_list else "No activities yet"

        # Format p-values
        goal_pvalue = f"Fluency: {goal.get('v', [0, 0])[0]:.2f}, Depth: {goal.get('v', [0, 0])[1]:.2f}"
        start_pvalue = f"Fluency: {start.get('v', [0, 0])[0]:.2f}, Depth: {start.get('v', [0, 0])[1]:.2f}"

        # Build activity-specific instructions
        activity_specific_instructions = ""
        if activity_custom_prompts:
            activity_specific_instructions = "\n\nACTIVITY-SPECIFIC CONTENT REQUESTS:\n"
            for position, custom_prompt in activity_custom_prompts.items():
                activity_name = activities[position]['activityName']
                activity_specific_instructions += f"- Activity {position} ({activity_name}): {custom_prompt}\n"

            # Debug: Print activity-specific prompts
            print("\n=== ACTIVITY-SPECIFIC PROMPTS ===")
            for position, custom_prompt in activity_custom_prompts.items():
                activity_name = activities[position]['activityName']
                print(f"Activity {position} ({activity_name}):")
                print(f"  {custom_prompt}")
            print("=================================\n")

        prompt = f"""I have created a lesson orchestration with the following details:

CONTEXT:
- Age Group: {age_group}
- Subject: {subject}
- Total Duration: {total_time} minutes
- Starting Point: {start_pvalue}
- Learning Goal: {goal_pvalue}

ACTIVITY SEQUENCE:
{activities_text}{activity_specific_instructions}

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
      "concreteExample": "GENERATE ACTUAL READY-TO-USE CONTENT based on the activity-specific request. Use clear numbering, proper line breaks (\\n), and spacing. Make it copy-paste ready for {age_group} students learning {subject}.",
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

CRITICAL RULES:
1. Provide exactly {len(activities)} activityEnhancement entries (positions 0-{len(activities)-1})
2. For "concreteExample": Generate ACTUAL ready-to-use content based on the activity-specific request - not descriptions. Use clear formatting with line breaks.
3. Resource types: video, worksheet, tool, simulation, article, reference, community
4. Return ONLY valid JSON, no other text."""

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


def create_llm_service(library=None) -> Optional[LLMService]:
    """
    Create an LLM service instance if API key is available
    Returns None if API key is not configured
    """
    try:
        return LLMService(library)
    except ValueError:
        # API key not configured - graceful degradation
        return None
