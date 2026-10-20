import sys
import argparse
from .memory import retain, recall, reflect

def main():
    parser = argparse.ArgumentParser(
        prog="hindsight",
        description="Temporal long-term memory engine for AI coding agents."
    )
    sub = parser.add_subparsers(dest="cmd")

    p_retain = sub.add_parser("retain", help="Retain a new fact in long-term memory")
    p_retain.add_argument("fact", help="Fact statement to store")
    p_retain.add_argument("-c", "--category", default="general", help="Category tag (e.g. architecture, config, auth)")
    p_retain.add_argument("-i", "--importance", type=int, default=5, help="Importance rating (1-10)")

    p_recall = sub.add_parser("recall", help="Recall facts ranked by BM25 match and recency decay")
    p_recall.add_argument("query", nargs="?", default="", help="Search query")
    p_recall.add_argument("-c", "--category", default="", help="Filter by category")
    p_recall.add_argument("-n", "--limit", type=int, default=10, help="Maximum results to return")

    sub.add_parser("reflect", help="Synthesize and reflect on stored memory anchors")

    args = parser.parse_args()

    if args.cmd == "retain":
        res = retain(args.fact, category=args.category, importance=args.importance)
        print(f"🧠 [Hindsight Retained #{res['id']}]: {res['fact']} (cat: {res['category']}, imp: {res['importance']})")
    elif args.cmd == "recall":
        results = recall(query=args.query, category=args.category, limit=args.limit)
        print(f"🔍 [Hindsight Recall for '{args.query}'] ({len(results)} matches):")
        for r in results:
            print(f"  • [#{r['id']} | score {r['score']} | {r['category']}]: {r['fact']}")
    elif args.cmd == "reflect":
        ref = reflect()
        print("💡 [Hindsight System Reflection]:")
        print(f"Total Memories: {ref['total_memories']} | Distinct Categories: {ref['categories_count']} | Avg Importance: {ref['avg_importance']}")
        print("Top Categories:")
        for c in ref["top_categories"]:
            print(f"  - {c['category']}: {c['count']}")
        print("Core Anchor Memories:")
        for a in ref["top_anchors"]:
            print(f"  - [#{a['id']} (imp:{a['importance']}, accessed:{a['accesses']})]: {a['fact']}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
