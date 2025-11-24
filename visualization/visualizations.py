import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from sklearn.manifold import TSNE

# ------------------------------
# AYARLAR
# ------------------------------
PCA_INPUT = "data/processed/pca_features.csv"
SCORED_INPUT = "data/processed/scored_data.csv"
LOADINGS_INPUT = "data/processed/pca_loadings_sorted.csv"
VARIANCE_INPUT = "data/processed/explained_variance_ratio.csv"
OUTPUT_DIR = "visualization/plots"

os.makedirs(OUTPUT_DIR, exist_ok=True)
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)

# ------------------------------
# 1️⃣ PCA Variance Plot
# ------------------------------
def plot_explained_variance():
    df_var = pd.read_csv(VARIANCE_INPUT, index_col=0)
    
    fig, ax = plt.subplots(1, 2, figsize=(14, 6))
    
    # Bar plot
    ax[0].bar(range(len(df_var)), df_var['explained_variance_ratio'], color='steelblue')
    ax[0].set_xlabel('PCA Component')
    ax[0].set_ylabel('Explained Variance Ratio')
    ax[0].set_title('Explained Variance by PCA Component')
    ax[0].set_xticks(range(len(df_var)))
    ax[0].set_xticklabels(df_var.index, rotation=45)
    
    # Cumulative plot
    cumsum = np.cumsum(df_var['explained_variance_ratio'])
    ax[1].plot(range(len(cumsum)), cumsum, marker='o', color='darkorange')
    ax[1].axhline(y=0.95, color='red', linestyle='--', label='95% Threshold')
    ax[1].set_xlabel('Number of Components')
    ax[1].set_ylabel('Cumulative Explained Variance')
    ax[1].set_title('Cumulative Explained Variance')
    ax[1].legend()
    ax[1].grid(True)
    
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/explained_variance.png", dpi=300, bbox_inches='tight')
    print("✓ Explained variance plot kaydedildi.")
    plt.close()

# ------------------------------
# 2️⃣ PCA Loadings Heatmap
# ------------------------------
def plot_pca_loadings():
    df_loadings = pd.read_csv(LOADINGS_INPUT, index_col=0)
    
    # En önemli 7 PCA
    top7_pca = df_loadings.columns[:7]
    df_subset = df_loadings[top7_pca]
    
    plt.figure(figsize=(12, 10))
    sns.heatmap(df_subset, cmap='coolwarm', center=0, annot=False, 
                cbar_kws={'label': 'Loading Value'})
    plt.title('PCA Loadings Heatmap (Top 7 Components)', fontsize=16)
    plt.xlabel('PCA Components')
    plt.ylabel('Original Features')
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/pca_loadings_heatmap.png", dpi=300, bbox_inches='tight')
    print("✓ PCA loadings heatmap kaydedildi.")
    plt.close()

# ------------------------------
# 3️⃣ PCA1 vs PCA2 Scatter Plot
# ------------------------------
def plot_pca_scatter():
    df = pd.read_csv(SCORED_INPUT)
    
    fig = px.scatter(df, x='PCA1', y='PCA2', color='is_anomaly',
                     hover_data=['Player', 'Pos', 'lof_score'],
                     color_discrete_map={0: 'blue', 1: 'red'},
                     labels={'is_anomaly': 'Anomaly'},
                     title='PCA1 vs PCA2 (Anomaly Detection)')
    
    fig.update_traces(marker=dict(size=8, opacity=0.7))
    fig.write_html(f"{OUTPUT_DIR}/pca_scatter_interactive.html")
    print("✓ PCA scatter plot (interactive) kaydedildi.")

# ------------------------------
# 4️⃣ LOF Score Distribution
# ------------------------------
def plot_lof_distribution():
    df = pd.read_csv(SCORED_INPUT)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(df['lof_score'], bins=50, color='purple', alpha=0.7, edgecolor='black')
    ax.axvline(df['lof_score'].median(), color='red', linestyle='--', 
               label=f'Median: {df["lof_score"].median():.2f}')
    ax.set_xlabel('LOF Score')
    ax.set_ylabel('Frequency')
    ax.set_title('Distribution of LOF Scores')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/lof_distribution.png", dpi=300, bbox_inches='tight')
    print("✓ LOF distribution plot kaydedildi.")
    plt.close()

# ------------------------------
# 5️⃣ Top 20 Players Bar Chart
# ------------------------------
def plot_top_players():
    df = pd.read_csv(SCORED_INPUT)
    df_sorted = df.sort_values('final_score', ascending=False).head(20)
    
    fig, ax = plt.subplots(figsize=(12, 8))
    colors = ['red' if x == 1 else 'steelblue' for x in df_sorted['is_anomaly']]
    
    ax.barh(df_sorted['Player'], df_sorted['final_score'], color=colors)
    ax.set_xlabel('Final Score')
    ax.set_ylabel('Player')
    ax.set_title('Top 20 Players by Final Score')
    ax.invert_yaxis()
    ax.grid(axis='x', alpha=0.3)
    
    # Legend
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor='red', label='Anomaly'),
                       Patch(facecolor='steelblue', label='Normal')]
    ax.legend(handles=legend_elements)
    
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/top20_players.png", dpi=300, bbox_inches='tight')
    print("✓ Top 20 players plot kaydedildi.")
    plt.close()

# ------------------------------
# 6️⃣ Position Distribution
# ------------------------------
def plot_position_distribution():
    df = pd.read_csv(SCORED_INPUT)
    
    fig, ax = plt.subplots(1, 2, figsize=(14, 6))
    
    # Count plot
    pos_counts = df['Pos'].value_counts()
    ax[0].bar(pos_counts.index, pos_counts.values, color='teal')
    ax[0].set_xlabel('Position')
    ax[0].set_ylabel('Count')
    ax[0].set_title('Player Count by Position')
    ax[0].grid(axis='y', alpha=0.3)
    
    # Box plot - Final Score by Position
    df.boxplot(column='final_score', by='Pos', ax=ax[1])
    ax[1].set_xlabel('Position')
    ax[1].set_ylabel('Final Score')
    ax[1].set_title('Final Score Distribution by Position')
    plt.suptitle('')
    
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/position_analysis.png", dpi=300, bbox_inches='tight')
    print("✓ Position analysis plot kaydedildi.")
    plt.close()

# ------------------------------
# 7️⃣ t-SNE Visualization
# ------------------------------
def plot_tsne():
    df = pd.read_csv(SCORED_INPUT)
    pca_cols = [col for col in df.columns if col.startswith('PCA')]
    
    X = df[pca_cols].values
    tsne = TSNE(n_components=2, random_state=42, perplexity=30)
    X_tsne = tsne.fit_transform(X)
    
    df['tsne1'] = X_tsne[:, 0]
    df['tsne2'] = X_tsne[:, 1]
    
    fig = px.scatter(df, x='tsne1', y='tsne2', color='is_anomaly',
                     hover_data=['Player', 'Pos'],
                     color_discrete_map={0: 'lightblue', 1: 'red'},
                     title='t-SNE Visualization of Players')
    
    fig.write_html(f"{OUTPUT_DIR}/tsne_visualization.html")
    print("✓ t-SNE visualization kaydedildi.")

# ------------------------------
# 8️⃣ Correlation Heatmap (PCA Components)
# ------------------------------
def plot_pca_correlation():
    df = pd.read_csv(SCORED_INPUT)
    pca_cols = [col for col in df.columns if col.startswith('PCA')][:7]
    
    corr = df[pca_cols].corr()
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr, annot=True, cmap='viridis', center=0, 
                square=True, linewidths=1)
    plt.title('Correlation Matrix - Top 7 PCA Components', fontsize=14)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/pca_correlation.png", dpi=300, bbox_inches='tight')
    print("✓ PCA correlation heatmap kaydedildi.")
    plt.close()

# ------------------------------
# ANA FONKSİYON
# ------------------------------
def main():
    print("\n--- 📊 Visualization Started ---\n")
    
    plot_explained_variance()
    plot_pca_loadings()
    plot_pca_scatter()
    plot_lof_distribution()
    plot_top_players()
    plot_position_distribution()
    plot_tsne()
    plot_pca_correlation()
    
    print("\n✅ Tüm grafikler oluşturuldu!")
    print(f"📁 Grafik klasörü: {OUTPUT_DIR}\n")

if __name__ == "__main__":
    main()