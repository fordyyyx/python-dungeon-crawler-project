Run pytest --cov=src/dungeon_crawler --cov-report=term-missing and show
me the full output. For any file below 90% coverage, tell me whether the
missing lines are inside main()'s game loop (acceptable, don't flag — it
relies on input()/print() and is only meant to be covered by the small
number of monkeypatch-based smoke tests, not exhaustively unit-tested)
or inside a standalone function (a real gap — list which function and
what behaviour looks untested).