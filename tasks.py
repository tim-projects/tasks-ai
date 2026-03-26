#!/usr/bin/env python3
import argparse
from tasks_ai.cli import TasksCLI

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="tasks-ai", 
        description="Tasks AI: Agent-optimized, Git-backed task lifecycle manager.", 
        formatter_class=argparse.RawDescriptionHelpFormatter, 
        add_help=True
    )
    parser.add_argument("-j", "--json", action="store_true", help="JSON output.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    subparsers.add_parser("init", help="Init tasks.")
    
    list_p = subparsers.add_parser("list", help="List tasks.")
    list_p.add_argument("--all", action="store_true")
    
    cur_p = subparsers.add_parser("current", help="Show active task.")
    cur_p.add_argument("filename", nargs="?")
    
    cp_p = subparsers.add_parser("checkpoint", help="Sync commits/notes.")
    cp_p.add_argument("filename", nargs="?")
    
    lk_p = subparsers.add_parser("link", help="Link tasks.")
    lk_p.add_argument("filename"); lk_p.add_argument("blocked_by")
    
    cr_p = subparsers.add_parser("create", help="Create task.")
    cr_p.add_argument("title"); cr_p.add_argument("--type", default="task", choices=["task", "issue"])
    cr_p.add_argument("--priority", "-p", type=int); cr_p.add_argument("--story")
    cr_p.add_argument("--tech"); cr_p.add_argument("--criteria", nargs="+")
    cr_p.add_argument("--plan", nargs="+"); cr_p.add_argument("--repro", nargs="+")
    
    mod_p = subparsers.add_parser("modify", help="Update task.")
    mod_p.add_argument("filename"); mod_p.add_argument("--title")
    mod_p.add_argument("--story"); mod_p.add_argument("--tech")
    mod_p.add_argument("--criteria", nargs="+"); mod_p.add_argument("--plan", nargs="+")
    mod_p.add_argument("--repro", nargs="+"); mod_p.add_argument("--notes")
    mod_p.add_argument("--progress"); mod_p.add_argument("--findings")
    mod_p.add_argument("--mitigations")
    
    mv_p = subparsers.add_parser("move", help="Move task.")
    mv_p.add_argument("filename"); mv_p.add_argument("status")
    
    del_p = subparsers.add_parser("delete", help="Permanently remove a task and its logs.")
    del_p.add_argument("filename"); del_p.add_argument("--confirm", help="Confirmation code.")
    
    rec_p = subparsers.add_parser("reconcile", help="Archive orphans.")
    rec_p.add_argument("target", nargs="?")
    
    args = parser.parse_args()
    cli = TasksCLI(as_json=args.json, command=args.command)
    
    if args.command == "init": cli.init()
    elif args.command == "create": 
        cli.create(args.title, args.type, args.priority, story=args.story, tech=args.tech, criteria=args.criteria, plan=args.plan, repro=args.repro)
    elif args.command == "modify": 
        cli.modify(args.filename, title=args.title, story=args.story, tech=args.tech, criteria=args.criteria, plan=args.plan, repro=args.repro, notes=args.notes, progress=args.progress, findings=args.findings, mitigations=args.mitigations)
    elif args.command == "move": cli.move(args.filename, args.status)
    elif args.command == "delete": cli.delete(args.filename, confirm=args.confirm)
    elif args.command == "list": cli.list(show_all=args.all)
    elif args.command == "current": cli.current(args.filename)
    elif args.command == "checkpoint": cli.checkpoint(args.filename)
    elif args.command == "link": cli.link(args.filename, args.blocked_by)
    elif args.command == "reconcile": cli.reconcile(args.target)
