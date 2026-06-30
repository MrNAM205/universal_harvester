from universal_harvester.diagnostics.network_diag import NetworkDiagnostics

def main():
    diag = NetworkDiagnostics()
    diag.run_all()

if __name__ == "__main__":
    main()
