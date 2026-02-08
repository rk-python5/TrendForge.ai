"""
Test script for LLM integration
Run this to verify Ollama is working correctly
"""

from tools.llm import llm
from tools.hashtag_tools import hashtag_generator
from config.settings import settings
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()


def test_llm():
    """Test LLM functionality"""
    
    console.print("\n[bold cyan]🤖 Testing Ollama LLM Integration...[/bold cyan]\n")
    
    # 1. Test basic generation
    console.print("[yellow]1. Testing basic text generation...[/yellow]")
    try:
        response = llm.generate("Say hello in one sentence.")
        console.print(f"   ✅ LLM Response: {response}\n")
    except Exception as e:
        console.print(f"   ❌ Error: {e}\n")
        console.print("[red]Make sure Ollama is running: ollama serve[/red]")
        return
    
    # 2. Test post generation
    console.print("[yellow]2. Generating a LinkedIn post...[/yellow]")
    topic = "The importance of learning AI in 2024"
    
    try:
        post = llm.generate_post(
            topic=topic,
            post_type="insight",
            tone="professional",
            user_name=settings.user_name,
            user_industry=settings.user_industry,
            user_expertise=settings.user_expertise
        )
        
        # Display the post in a nice panel
        console.print("\n")
        console.print(Panel(
            post,
            title="[bold green]Generated LinkedIn Post[/bold green]",
            border_style="green",
            padding=(1, 2)
        ))
        
    except Exception as e:
        console.print(f"   ❌ Error generating post: {e}\n")
        return
    
    # 3. Test hashtag generation
    console.print("\n[yellow]3. Generating hashtags...[/yellow]")
    try:
        hashtags = hashtag_generator.generate(topic, post, count=5)
        console.print(f"   ✅ Generated hashtags: {hashtags}\n")
    except Exception as e:
        console.print(f"   ❌ Error generating hashtags: {e}\n")
    
    # 4. Test different post types
    console.print("[yellow]4. Testing different post types...[/yellow]\n")
    
    post_types = ["tip", "question", "story"]
    
    for post_type in post_types:
        try:
            console.print(f"   Generating {post_type} post...")
            test_post = llm.generate_post(
                topic="AI tools for productivity",
                post_type=post_type,
                tone="casual"
            )
            console.print(f"   ✅ {post_type.title()} post generated ({len(test_post)} chars)\n")
        except Exception as e:
            console.print(f"   ❌ Error with {post_type}: {e}\n")
    
    # 5. Test improvement
    console.print("[yellow]5. Testing post improvement...[/yellow]")
    try:
        improved = llm.improve_post(
            original_post=post,
            feedback="Make it shorter and add more specific examples"
        )
        console.print("   ✅ Post improvement working\n")
    except Exception as e:
        console.print(f"   ❌ Error improving post: {e}\n")
    
    # Summary
    console.print("\n[bold green]✅ LLM Integration Test Complete![/bold green]")
    console.print("\n[dim]Your Ollama LLM is ready to generate LinkedIn posts![/dim]\n")
    
    # Show current settings
    console.print("[yellow]Current Settings:[/yellow]")
    console.print(f"   Model: {settings.ollama_model}")
    console.print(f"   Base URL: {settings.ollama_base_url}")
    console.print(f"   User: {settings.user_name}")
    console.print(f"   Industry: {settings.user_industry}\n")


if __name__ == "__main__":
    test_llm()
