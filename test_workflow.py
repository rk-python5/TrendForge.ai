"""
Test script for LangGraph workflow
"""

from graph.workflow import workflow
from storage.database import db
from utils.helpers import format_post_for_display
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


def test_workflow():
    """Test the complete LangGraph workflow"""
    
    console.print("\n[bold cyan]🔄 Testing LangGraph Workflow...[/bold cyan]\n")
    
    # Test 1: Direct topic workflow
    console.print("[yellow]Test 1: Direct Topic → Post Generation[/yellow]\n")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Generating post...", total=None)
        
        try:
            result = workflow.run_with_topic(
                topic="The importance of continuous learning in tech",
                post_type="insight",
                tone="professional"
            )
            
            progress.update(task, completed=True)
            
        except Exception as e:
            console.print(f"\n❌ Error: {e}\n")
            return
    
    # Check result status
    if result["status"] == "error":
        console.print(f"\n[red]❌ Workflow failed: {result['error']}[/red]\n")
        return
    
    # Display the generated post
    formatted_post = format_post_for_display(
        result["content"],
        result["hashtags"]
    )
    
    console.print(Panel(
        formatted_post,
        title=f"[bold green]Generated Post (ID: {result['post_id']})[/bold green]",
        subtitle=f"Status: {result['status']} | Score: {result.get('review_score', 'N/A')}/10",
        border_style="green",
        padding=(1, 2)
    ))
    
    # Show workflow details
    details_table = Table(title="\nWorkflow Details")
    details_table.add_column("Property", style="cyan")
    details_table.add_column("Value", style="white")
    
    details_table.add_row("Topic", result["topic"])
    details_table.add_row("Post Type", result["post_type"])
    details_table.add_row("Tone", result["tone"])
    details_table.add_row("Word Count", str(result["word_count"]))
    details_table.add_row("Character Count", str(result["char_count"]))
    details_table.add_row("Review Score", f"{result.get('review_score', 'N/A')}/10")
    details_table.add_row("Status", result["status"])
    details_table.add_row("Post ID", str(result["post_id"]))
    
    console.print(details_table)
    
    # Test 2: Theme-based workflow (with idea generation)
    console.print("\n[yellow]Test 2: Theme → Ideas → Post Generation[/yellow]\n")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Generating ideas and post...", total=None)
        
        try:
            result2 = workflow.run_with_theme(
                theme="Remote work and productivity",
                post_type="tip",
                tone="casual"
            )
            
            progress.update(task, completed=True)
            
        except Exception as e:
            console.print(f"\n❌ Error: {e}\n")
            return
    
    # Display generated ideas
    if result2.get("post_ideas"):
        ideas_table = Table(title="\nGenerated Ideas")
        ideas_table.add_column("#", style="cyan", width=5)
        ideas_table.add_column("Idea", style="white")
        
        for i, idea in enumerate(result2["post_ideas"], 1):
            style = "bold green" if idea == result2["selected_idea"] else "white"
            ideas_table.add_row(str(i), f"[{style}]{idea}[/{style}]")
        
        console.print(ideas_table)
    
    # Display the second post
    formatted_post2 = format_post_for_display(
        result2["content"],
        result2["hashtags"]
    )
    
    console.print(Panel(
        formatted_post2,
        title=f"[bold green]Generated Post (ID: {result2['post_id']})[/bold green]",
        subtitle=f"Selected Idea: {result2['selected_idea']}",
        border_style="green",
        padding=(1, 2)
    ))
    
    # Database stats
    console.print("\n[yellow]Database Statistics:[/yellow]")
    stats = db.get_stats()
    
    stats_table = Table()
    stats_table.add_column("Metric", style="cyan")
    stats_table.add_column("Count", style="green")
    
    for key, value in stats.items():
        stats_table.add_row(key.replace("_", " ").title(), str(value))
    
    console.print(stats_table)
    
    # Summary
    console.print("\n[bold green]✅ LangGraph Workflow Test Complete![/bold green]")
    console.print("\n[bold]What just happened:[/bold]")
    console.print("1. ✅ Created initial state")
    console.print("2. ✅ Generated post ideas (Test 2)")
    console.print("3. ✅ Selected topic")
    console.print("4. ✅ Generated post content")
    console.print("5. ✅ Self-reviewed the post")
    console.print("6. ✅ Saved to database")
    console.print("\n[dim]Your agentic workflow is now operational! 🚀[/dim]\n")


if __name__ == "__main__":
    test_workflow()
