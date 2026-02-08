"""
Test script for Content Generator Agent
"""

from agents.content_generator import content_agent
from storage.database import db
from utils.helpers import format_post_for_display, get_post_metrics
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def test_content_agent():
    """Test the content generator agent"""
    
    console.print("\n[bold cyan]🤖 Testing Content Generator Agent...[/bold cyan]\n")
    
    # 1. Generate post ideas
    console.print("[yellow]1. Generating post ideas...[/yellow]")
    try:
        ideas = content_agent.generate_post_ideas("AI and automation", count=3)
        
        table = Table(title="Generated Post Ideas")
        table.add_column("#", style="cyan", width=5)
        table.add_column("Topic Idea", style="white")
        
        for i, idea in enumerate(ideas, 1):
            table.add_row(str(i), idea)
        
        console.print(table)
        console.print()
        
    except Exception as e:
        console.print(f"   ❌ Error: {e}\n")
        return
    
    # 2. Generate a post
    console.print("[yellow]2. Generating a full LinkedIn post...[/yellow]")
    try:
        topic = ideas[0] if ideas else "The future of AI in business"
        
        result = content_agent.generate_post(
            topic=topic,
            post_type="insight",
            tone="professional",
            save_to_db=True,
            generate_hashtags=True
        )
        
        # Display the post
        formatted_post = format_post_for_display(
            result["content"],
            result["hashtags"]
        )
        
        console.print(Panel(
            formatted_post,
            title=f"[bold green]Generated Post (ID: {result['post_id']})[/bold green]",
            subtitle=f"Topic: {result['topic']}",
            border_style="green",
            padding=(1, 2)
        ))
        
        # Show metrics
        metrics = get_post_metrics(result["content"])
        console.print(f"\n   📊 Words: {metrics['word_count']} | Characters: {metrics['character_count']} | Reading time: ~{metrics['reading_time_seconds']}s")
        console.print(f"   #️⃣ Hashtags: {result['hashtags']}\n")
        
        post_id = result["post_id"]
        
    except Exception as e:
        console.print(f"   ❌ Error: {e}\n")
        return
    
    # 3. Generate variations
    console.print("[yellow]3. Generating post variations...[/yellow]")
    try:
        variations = content_agent.generate_variations(
            topic="Tips for remote work productivity",
            count=2,
            post_type="tip",
            tone="casual"
        )
        
        console.print(f"   ✅ Generated {len(variations)} variations\n")
        
        for i, var in enumerate(variations, 1):
            console.print(f"   [cyan]Variation {i}:[/cyan] {var['word_count']} words\n")
        
    except Exception as e:
        console.print(f"   ❌ Error: {e}\n")
    
    # 4. Review the post
    console.print("[yellow]4. Self-reviewing the post...[/yellow]")
    try:
        review = content_agent.review_post(result["content"])
        
        console.print(Panel(
            review["review"],
            title="[bold blue]Post Review[/bold blue]",
            border_style="blue",
            padding=(1, 2)
        ))
        
        if "score" in review:
            console.print(f"\n   📈 Score: {review['score']}/10\n")
        
    except Exception as e:
        console.print(f"   ❌ Error: {e}\n")
    
    # 5. Improve the post
    console.print("[yellow]5. Improving the post...[/yellow]")
    try:
        improved = content_agent.improve_post(
            post_id=post_id,
            feedback="Make it more engaging and add a specific example",
            save_as_new=True
        )
        
        console.print(f"   ✅ Improved version created (ID: {improved['post_id']})\n")
        
    except Exception as e:
        console.print(f"   ❌ Error: {e}\n")
    
    # 6. Show database stats
    console.print("[yellow]6. Database statistics...[/yellow]")
    stats = db.get_stats()
    
    stats_table = Table(title="Post Statistics")
    stats_table.add_column("Metric", style="cyan")
    stats_table.add_column("Count", style="green")
    
    for key, value in stats.items():
        stats_table.add_row(key.replace("_", " ").title(), str(value))
    
    console.print(stats_table)
    
    console.print("\n[bold green]✅ Content Generator Agent Test Complete![/bold green]")
    console.print("\n[dim]Your agent can now generate, review, and improve LinkedIn posts![/dim]\n")


if __name__ == "__main__":
    test_content_agent()
