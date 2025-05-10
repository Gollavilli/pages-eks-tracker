#!/usr/bin/env python3
import os
import sys
import json
import yaml
import requests
from datetime import datetime
from github import Github

# Configuration - Add your components here
COMPONENTS = {
    "bottlerocket-os": {
        "type": "github",
        "github_repo": "bottlerocket-os/bottlerocket",
        "description": "Purpose-built OS for running containers on EKS",
        "special": True
    },
    "karpenter": {
        "type": "helm",
        "repo": "oci://public.ecr.aws/karpenter",
        "chart": "karpenter",
        "github_repo": "aws/karpenter-provider-aws",
        "description": "Kubernetes Node Autoscaler"
    },
    "datadog": {
        "type": "helm",
        "repo": "https://helm.datadoghq.com",
        "chart": "datadog",
        "github_repo": "DataDog/helm-charts",
        "chart_path": "charts/datadog",
        "description": "Datadog Monitoring Agent"
    },
    "cert-manager": {
        "type": "helm",
        "repo": "https://charts.jetstack.io",
        "chart": "cert-manager",
        "github_repo": "cert-manager/cert-manager",
        "description": "Automatically provision and manage TLS certificates"
    },
    "aws-for-fluent-bit": {
        "type": "helm",
        "repo": "https://aws.github.io/eks-charts",
        "chart": "aws-for-fluent-bit",
        "github_repo": "aws/eks-charts",
        "chart_path": "stable/aws-for-fluent-bit",
        "description": "Log processor and forwarder for AWS"
    },
    "aws-load-balancer-controller": {
        "type": "helm",
        "repo": "https://aws.github.io/eks-charts",
        "chart": "aws-load-balancer-controller",
        "github_repo": "kubernetes-sigs/aws-load-balancer-controller",
        "description": "AWS Load Balancer Controller"
    },
    "ingress-nginx": {
        "type": "helm",
        "repo": "https://kubernetes.github.io/ingress-nginx",
        "chart": "ingress-nginx",
        "github_repo": "kubernetes/ingress-nginx",
        "description": "Ingress controller for Kubernetes using NGINX as a reverse proxy"
    },
    "adot-exporter-for-eks-on-ec2": {
        "type": "helm",
        "repo": "https://aws-observability.github.io/aws-otel-helm-charts",
        "chart": "adot-exporter-for-eks-on-ec2",
        "github_repo": "aws-observability/aws-otel-helm-charts",
        "description": "AWS Distro for OpenTelemetry (ADOT) Collector"
    },
    "wiz": {
        "type": "helm",
        "repo": "https://github.com/wiz-sec/charts",
        "chart": "wiz",
        "github_repo": "wiz-sec/charts",
        "description": "Wiz Security Platform for Kubernetes"
    }
}

def get_helm_chart_version(repo_url, chart_name):
    try:
        # Add helm repo
        os.system(f"helm repo add temp-repo {repo_url} > /dev/null 2>&1")
        os.system("helm repo update > /dev/null 2>&1")
        
        # Get chart info
        result = os.popen(f"helm search repo temp-repo/{chart_name} -o json").read()
        chart_info = json.loads(result)
        
        if chart_info and len(chart_info) > 0:
            return {
                "version": chart_info[0]["version"],
                "app_version": chart_info[0]["app_version"],
                "updated": chart_info[0]["created"]
            }
        else:
            return {"version": "N/A", "app_version": "N/A", "updated": "N/A"}
    except Exception as e:
        print(f"Error fetching Helm chart version for {chart_name}: {str(e)}", file=sys.stderr)
        return {"version": "Error", "app_version": "Error", "updated": "N/A"}
    finally:
        # Clean up repo
        os.system("helm repo remove temp-repo > /dev/null 2>&1")

def get_github_release_info(repo_name):
    try:
        g = Github(os.environ.get("GITHUB_TOKEN"))
        repo = g.get_repo(repo_name)
        releases = repo.get_releases()
        
        if releases.totalCount > 0:
            latest_release = releases[0]
            return {
                "latest_release": latest_release.tag_name,
                "published_at": latest_release.published_at.strftime("%Y-%m-%d") if latest_release.published_at else "N/A",
                "url": latest_release.html_url
            }
        else:
            return {"latest_release": "No releases", "published_at": "N/A", "url": f"https://github.com/{repo_name}/releases"}
    except Exception as e:
        print(f"Error fetching GitHub release info for {repo_name}: {str(e)}", file=sys.stderr)
        return {"latest_release": "Error", "published_at": "N/A", "url": f"https://github.com/{repo_name}/releases"}

def main():
    output_dir = os.environ.get("OUTPUT_DIR", ".")
    
    results = []
    
    for name, config in COMPONENTS.items():
        print(f"Checking {name}...", file=sys.stderr)
        
        if config["type"] == "helm":
            helm_info = get_helm_chart_version(config["repo"], config["chart"])
            github_info = get_github_release_info(config["github_repo"])
            
            results.append({
                "name": name,
                "description": config["description"],
                "helm_chart": config["chart"] if "chart" in config else "",
                "helm_version": helm_info["version"],
                "app_version": helm_info["app_version"],
                "helm_updated": helm_info["updated"],
                "github_release": github_info["latest_release"],
                "github_date": github_info["published_at"],
                "github_url": github_info["url"],
                "helm_repo": config["repo"] if "repo" in config else "",
                "special": config.get("special", False)
            })
        elif config["type"] == "github":
            github_info = get_github_release_info(config["github_repo"])
            
            results.append({
                "name": name,
                "description": config["description"],
                "helm_chart": "",
                "helm_version": "",
                "app_version": "",
                "helm_updated": "",
                "github_release": github_info["latest_release"],
                "github_date": github_info["published_at"],
                "github_url": github_info["url"],
                "helm_repo": "",
                "special": config.get("special", False)
            })
    
    # Sort by name
    results.sort(key=lambda x: x["name"])
    
    # Save data as JSON
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, 'data.json'), 'w') as f:
        json.dump({
            "generated_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "components": results
        }, f, indent=2)
    
    print(f"Data saved to {os.path.join(output_dir, 'data.json')}")

if __name__ == "__main__":
    main()
