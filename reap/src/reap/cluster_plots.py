import pathlib
import matplotlib.pyplot as plt
import seaborn as sns
import torch
import warnings
from typing import Any
import numpy as np
import pandas as pd

def _save_fig(fig, plot_path: pathlib.Path):
    fig.savefig(f"{plot_path}.png", dpi=600, bbox_inches='tight')
    # fig.savefig(f"{plot_path}.pdf", dpi=600, bbox_inches='tight')
    
def _plot_layer_clusters(cluster_label: torch.Tensor, plot_path: pathlib.Path):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        fig, ax = plt.subplots(figsize=(12, 6))
        cluster_sizes = torch.bincount(cluster_label).cpu().numpy()
        sns.barplot(x=range(len(cluster_sizes)), y=cluster_sizes, ax=ax)
        ax.set_xlabel("Cluster")
        ax.set_ylabel("Cluster Size")
        ax.tick_params(axis='x', labelrotation=90)
        _save_fig(fig, plot_path)

def plot_cluster_analysis(
    cluster_labels: dict[int, torch.Tensor],
    plot_dir: pathlib.Path,
    skip_first: bool,
    skip_last: bool,
):
    # layerwise clusters
    total_singletons = []
    total_non_singletons = []
    total_non_singleton_sizes = []
    num_remaining_experts_per_layer = []
    num_layers = len(cluster_labels)
    for i, (layer, cluster_label) in enumerate(cluster_labels.items()):
        layer_plot_dir = plot_dir / "layers" / f"layer_{layer}"
        layer_plot_dir.parent.mkdir(parents=True, exist_ok=True)
        _plot_layer_clusters(cluster_label, layer_plot_dir)
        cluster_sizes = torch.bincount(cluster_label)
        non_singletons = torch.argwhere(cluster_sizes != 1)
        num_singletons = len(torch.unique(cluster_label)) - non_singletons.shape[0]
        total_singletons.append(num_singletons)
        total_non_singletons.append(non_singletons.shape[0])
        size_non_singletons = (cluster_sizes[cluster_sizes!=1]).sum().item()
        total_non_singleton_sizes.append(size_non_singletons)

        if (skip_first and i == 0) or (skip_last and i == num_layers - 1):
            num_remaining_experts = len(cluster_label)
        else:
            num_remaining_experts = len(torch.unique(cluster_label))
        num_remaining_experts_per_layer.append(num_remaining_experts)


    average_non_singleton_sizes = torch.tensor(total_non_singleton_sizes) / torch.tensor(total_non_singletons)
    average_non_singleton_sizes = average_non_singleton_sizes.nan_to_num(0)
    average_non_singleton_sizes = average_non_singleton_sizes.tolist()
    # overall plots
    # singletons
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x=list(cluster_labels.keys()), y=total_singletons, ax=ax)
    ax.set_xlabel("Layer")
    ax.set_ylabel("Number of Singletons")
    _save_fig(fig, plot_dir / "singletons_per_layer")

    # non-singletons
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x=list(cluster_labels.keys()), y=total_non_singletons, ax=ax)
    ax.set_xlabel("Layer")
    ax.set_ylabel("Number of Non-Singletons")
    _save_fig(fig, plot_dir / "non_singletons_per_layer")

    # non-singleton sizes
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x=list(cluster_labels.keys()), y=total_non_singleton_sizes, ax=ax)
    ax.set_xlabel("Layer")
    ax.set_ylabel("Non-Singleton Clusters Sizes")
    _save_fig(fig, plot_dir / "non_singleton_sizes_per_layer")
    
    # average non-singleton sizes
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x=list(cluster_labels.keys()), y=average_non_singleton_sizes, ax=ax)
    ax.set_xlabel("Layer")
    ax.set_ylabel("Average Non-Singleton Clusters Sizes")
    _save_fig(fig, plot_dir / "average_non_singleton_sizes_per_layer")

    # merged experts per layer
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x=list(cluster_labels.keys()), y=num_remaining_experts_per_layer, ax=ax)
    ax.set_xlabel("Layer")
    ax.set_ylabel("Number of Remaining Experts")
    _save_fig(fig, plot_dir / "num_remaining_experts_per_layer")


def plot_expert_activation_distribution(
    observer_data: dict[int, dict[str, Any]],
    output_dir: pathlib.Path,
):
    """
    Plots expert activation distribution for each data source and saves to Excel.
    
    Args:
        observer_data: The observation data containing expert frequencies.
        output_dir: Directory to save the plots and Excel file.
    """
    activation_dir = output_dir / "activation_distributions"
    activation_dir.mkdir(parents=True, exist_ok=True)
    
    layer_indices = sorted([k for k in observer_data.keys() if isinstance(k, int)])
    if not layer_indices:
        print("No layer data found in observer_data.")
        return

    # Identify all data sources across all layers
    all_sources = set()
    for layer in layer_indices:
        if "expert_frequency_by_source" in observer_data[layer]:
            all_sources.update(observer_data[layer]["expert_frequency_by_source"].keys())
    
    sources = sorted(list(all_sources))
    plot_sources = sources + ["all"]
    
    num_experts = observer_data[layer_indices[0]]["expert_frequency"].shape[0]
    
    # Data containers for Excel export
    # Key: source name, Value: DataFrame (Rows: Layer, Cols: Expert ID)
    excel_data = {s: pd.DataFrame(index=layer_indices, columns=range(num_experts)) for s in plot_sources}

    for layer in layer_indices:
        layer_data = observer_data[layer]
        freq_by_source = layer_data.get("expert_frequency_by_source", {})
        
        # Create subplots
        n_plots = len(plot_sources)
        cols = 3
        rows = (n_plots + cols - 1) // cols
        
        fig, axes = plt.subplots(rows, cols, figsize=(cols * 6, rows * 4), squeeze=False)
        plt.subplots_adjust(hspace=0.4, wspace=0.3)
        
        for i, source in enumerate(plot_sources):
            r, c = i // cols, i % cols
            ax = axes[r, c]
            
            if source == "all":
                freq = layer_data["expert_frequency"].cpu().numpy()
            else:
                freq = freq_by_source.get(source, torch.zeros(num_experts, dtype=torch.long)).cpu().numpy()
            
            # Save to Excel data
            excel_data[source].loc[layer] = freq
            
            # Plot
            sns.barplot(x=list(range(num_experts)), y=freq, ax=ax)
            ax.set_title(f"Source: {source}")
            ax.set_xlabel("Expert ID")
            ax.set_ylabel("Activation Frequency")
            if num_experts > 32:
                ax.set_xticks(range(0, num_experts, num_experts // 32 or 1))
            ax.tick_params(axis='x', labelrotation=90)
            
        # Hide empty subplots
        for i in range(n_plots, rows * cols):
            r, c = i // cols, i % cols
            axes[r, c].axis('off')
            
        fig.suptitle(f"Layer {layer} Expert Activation Distribution", fontsize=16)
        _save_fig(fig, activation_dir / f"layer_{layer}_activation")
        plt.close(fig)

    # Save to Excel
    excel_path = output_dir / "expert_activations.xlsx"
    with pd.ExcelWriter(excel_path) as writer:
        for source, df in excel_data.items():
            # Use source name as sheet name (limit to 31 chars for Excel)
            sheet_name = str(source)[:31]
            df.to_excel(writer, sheet_name=sheet_name)
    
    print(f"Activation plots saved to {activation_dir}")
    print(f"Activation data saved to {excel_path}")
