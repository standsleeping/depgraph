from depgraph.cli import parse_args
from depgraph.logger import setup_logger

def main() -> None:
    (
        file_path,
        depth,
        log_level,
        log_file,
        scope_filter,
    ) = parse_args()

    # Set up logging first
    logger = setup_logger(level=log_level, log_file=log_file)

    # Import other modules after logger is configured
    from depgraph.analyze_file import analyze_file
    from depgraph.formatter import print_analysis
    from depgraph.scope_data import FileAnalysis, ScopeInfo
    from depgraph.assignment_analyzer import ScopeAssignmentAnalyzer
    logger.debug("Starting analysis with parameters:")
    logger.debug(f"  file_path: {file_path}")
    logger.debug(f"  depth: {depth}")
    logger.debug(f"  log_level: {log_level}")
    logger.debug(f"  log_file: {log_file}")
    if scope_filter:
        logger.debug(f"  scope_filter: {scope_filter}")

    logger.info(f"Analyzing file '{file_path}'")
    file_analysis: FileAnalysis = analyze_file(file_path=file_path, depth=depth)

    module_scope_info: ScopeInfo
    if scope_filter:
        module_scope_info = file_analysis.scopes[scope_filter]
    else:
        module_scope_info = file_analysis.scopes["<module>"]

    analyzer = ScopeAssignmentAnalyzer()

    assignments = analyzer.analyze_scope(module_scope_info)

    logger.info("Analysis complete!")

    print_analysis(
        analysis=file_analysis,
        scope_filter=scope_filter,
        assignments=assignments,
    )


if __name__ == "__main__":
    main()
