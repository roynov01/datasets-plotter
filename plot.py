import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

PLOT_SIZE = (9, 6)
TISSUES = ["all tissues", "pancreas", "intestine", "liver", "thyroid"]
ORGANISMS = ["mouse", "human"]


def import_datasets(path=r'datasets'):
    datasets = {}

    ts_pancreas = pd.read_csv(f'{path}/TabulaSapiens_pancreas.csv')
    datasets["ts_pancreas"] = ts_pancreas
    ts_liver = pd.read_csv(f'{path}/TabulaSapiens_liver.csv')
    datasets["ts_liver"] = ts_liver
    ts_intestine = pd.read_csv(f'{path}/TabulaSapiens_intestine.csv')
    datasets["ts_intestine"] = ts_intestine

    tm_pancreas = pd.read_csv(f'{path}/tabulamuris_facs_pancreas.csv')
    tm_pancreas = pd.melt(tm_pancreas, id_vars=['gene'], var_name='celltype', value_name='expression')
    datasets["tm_pancreas"] = tm_pancreas

    hpa = pd.read_csv(f'{path}/human_protein_atlas_expression.csv')
    datasets["hpa"] = hpa

    yotams_visium_zonation = pd.read_csv(f'{path}/yotams_visium_zonation.csv')
    yotams_visium_zonation = pd.melt(yotams_visium_zonation, id_vars=['gene'], var_name='zone', value_name='expression')
    datasets["yotams_visium_zonation"] = yotams_visium_zonation

    rachel_zwick_human = pd.read_csv(f'{path}/rachel_zwick_human.csv')
    rachel_zwick_human = pd.melt(rachel_zwick_human, id_vars=['gene', 'section'], var_name='celltype', value_name='expression')
    datasets["rachel_zwick_human"] = rachel_zwick_human

    rachel_zwick_mouse = pd.read_csv(f'{path}/rachel_zwick_mouse.csv')
    rachel_zwick_mouse = pd.melt(rachel_zwick_mouse, id_vars=['gene', 'section'], var_name='celltype', value_name='expression')
    datasets["rachel_zwick_mouse"] = rachel_zwick_mouse

    innas = pd.read_csv(f'{path}/mouse_intestines_sc_innas.csv')
    innas = pd.melt(innas, id_vars=['gene'], var_name='celltype', value_name='expression')
    datasets["innas"] = innas

    yotams_sc_sigmat = pd.read_csv(f'{path}/human_intestines_sc.csv')
    yotams_sc_sigmat = pd.melt(yotams_sc_sigmat, id_vars=['gene'], var_name='celltype', value_name='expression')
    datasets["yotams_sc_sigmat"] = yotams_sc_sigmat

    apap = pd.read_csv(f'{path}/liver_from_APAP.csv')
    apap = pd.melt(apap, id_vars=['gene'], var_name='celltype', value_name='expression')
    datasets["apap"] = apap

    human_apicome = pd.read_csv(f'{path}/human_apicome.csv')
    human_apicome = pd.melt(human_apicome, id_vars=['gene'], var_name='apicome', value_name='expression')
    datasets["human_apicome"] = human_apicome

    mouse_apicome = pd.read_csv(f'{path}/mouse_apicome.csv')
    mouse_apicome = pd.melt(mouse_apicome, id_vars=['gene'], var_name='apicome', value_name='expression')
    datasets["mouse_apicome"] = mouse_apicome

    thyroid_kang = pd.read_csv(f'{path}/thyroid_sig_mat.csv')
    thyroid_kang = pd.melt(thyroid_kang, id_vars=['gene'], var_name='celltype', value_name='expression')
    datasets["thyroid_Kang"] = thyroid_kang

    return datasets


def make_plots(organism, organ, gene, datasets):
    """returns list of plots"""
    plots, names = [], []
    if organ == "all tissues":
        if organism == "human":
            plots.append(hpa(datasets['hpa'], gene))
            names += ['hpa']
        elif organism == "mouse":
            pass
    if organ == "intestine":
        if organism == "human":
            plots.append(tabula_sapiens(datasets['ts_intestine'], gene, organ))
            plots.append(yotams_sc(datasets['yotams_sc_sigmat'], gene))
            plots.append(yotams_visium(datasets['yotams_visium_zonation'], gene))
            names += ['ts_intestine', 'yotams_sc_sigmat', 'yotams_visium_zonation']
        elif organism == "mouse":
            plots.append(inna(datasets['innas'], gene))
            names += ['innas']
        plots.append(apicome(datasets[f'{organism}_apicome'], gene, organism))
        plots.append(rachel_zwick(datasets[f'rachel_zwick_{organism}'], gene, organism))
        names += [f'{organism}_apicome', f'rachel_zwick_{organism}']
    if organ == "pancreas":
        if organism == "human":
            plots.append(tabula_sapiens(datasets['ts_pancreas'], gene, organ))
            names += ['ts_pancreas']
        elif organism == "mouse":
            plots.append(tabula_muris(datasets['tm_pancreas'], gene, organ))
            names += ['tm_pancreas']
    if organ == "liver":
        if organism == "human":
            plots.append(tabula_sapiens(datasets['ts_liver'], gene, organ))
            names += ['ts_liver']
        elif organism == "mouse":
            plots.append(shani(datasets['apap'], gene))
            names += ['apap']
    if organ == "thyroid" and organism == "human":
        plots.append(plot_thyroid(datasets['thyroid_Kang'], gene))
        names += ['thyroid_Kang']

    names = [names[i] for i in range(len(plots)) if plots[i] is not None]
    plots = [plot for plot in plots if plot is not None]
    return plots, names


def bar(df, gene, title, x="celltype", y="expression", organism=''):
    if gene not in df['gene'].values:
        return
    gene_df = df[df['gene'] == gene]
    plt.figure(figsize=PLOT_SIZE)
    print(gene_df.head())
    ax = sns.barplot(data=gene_df, x=x, y=y, color='blue', edgecolor='black')
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, horizontalalignment='right')
    plt.xlabel('')
    plt.ylabel('Expression')
    plt.title(f'{organism}{title} - {gene}')
    plt.tight_layout()
    return plt.gcf()


def shani(df, gene):
    return bar(df, gene, "Liver atlas (2020)")


def yotams_visium(df, gene):
    return bar(df, gene, "Yotams visium", x="zone")


def apicome(df, gene, organism):
    return bar(df, gene, " Intestines (Yotams visium)", x="apicome", organism=organism)


def inna(df, gene):
    return bar(df, gene, "mouse intestine")


def hpa(df, gene):
    if gene not in df['gene'].values:
        return
    gene_df = df[df['gene'] == gene]
    plt.figure(figsize=PLOT_SIZE)
    gene_df = gene_df.sort_values('organ')
    ax = sns.barplot(data=gene_df, x='tissue', y='nTPM', hue='organ', edgecolor='black', dodge=False)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, horizontalalignment='right')
    plt.xlabel('')
    plt.ylabel('nTPM')
    plt.title(f'human protein atlas - {gene}')
    plt.tight_layout()
    plt.legend([], [], frameon=False)
    return plt.gcf()


def tabula_muris(df, gene, organ="pancreas"):
    if gene not in df['gene'].values:
        return
    gene_df = df[df['gene'] == gene]
    plt.figure(figsize=PLOT_SIZE)
    ax = sns.barplot(data=gene_df, x='celltype', y='expression', color='blue', edgecolor='black')
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, horizontalalignment='right')
    plt.xlabel('')
    plt.ylabel('Expression')
    plt.title(f'mouse {organ} (Tabula Muris) - {gene}')
    plt.tight_layout()
    return plt.gcf()


def tabula_sapiens(df, gene, organ):
    if gene not in df['gene'].values:
        return
    gene_df = df[df['gene'] == gene]
    plt.figure(figsize=PLOT_SIZE)
    ax = sns.barplot(data=gene_df, x='celltype', y='expression', color='blue', edgecolor='black')
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, horizontalalignment='right')
    plt.xlabel('')
    plt.ylabel('Expression')
    plt.title(f'human {organ} (Tabula Sapiens) - {gene}')
    plt.tight_layout()
    return plt.gcf()


def yotams_sc(df, gene):
    return bar(df, gene, "Human intestines (single cell)")


def rachel_zwick(df, gene, organism):
    if gene not in df['gene'].values:
        return
    gene_df = df[df['gene'] == gene]
    plt.figure(figsize=PLOT_SIZE)
    ax = sns.lineplot(data=gene_df, x="section", y="expression", hue="celltype")
    ax.set_xticks(gene_df["section"].unique())
    labels = ['' for _ in range(len(gene_df["section"].unique()))]
    labels[0], labels[-1] = 'Duodenum', "terminal ileum"
    ax.set_xticklabels(labels)
    plt.xlabel('')
    plt.ylabel('Expression')
    plt.title(f'{organism} intestine sectiones - {gene}')
    plt.tight_layout()
    plt.legend(loc='upper right')
    return plt.gcf()


def plot_thyroid(df, gene):
    return bar(df, gene, "Human thyroid (Keng et al.)")


# x = import_datasets()
# gene = "RPS14"

# df = x["rachel_zwick_human"]
# fig = rachel_zwick(df, gene, "human")
# df = x["rachel_zwick_mouse"]
# fig = rachel_zwick(df, gene, "mouse")
# df = x["yotams_visium_zonation"]
# fig = yotams_visium(df, gene)
# df = x["shani_zonation"]
# fig = shani(df, gene)
# df = x["mouse_apicome"]
# fig = apicome(df, gene, "mouse")
# df = x["innas"]
# fig = inna(df, gene)
# df = x["hpa"]
# fig = hpa(df, gene)
# df = x["tm_pancreas"]
# fig = tabula_muris(df, gene, "pancreas")
# df = x["ts_pancreas"]
# fig = tabula_sapiens(df, gene, "pancreas")
# df = x["ts_intestine"]
# fig = tabula_sapiens(df, gene, "intestine")
# df = x["ts_liver"]
# fig = tabula_sapiens(df, gene, "liver")
# df = x["yotams_sc_sigmat"]
# fig = yotams_sc(df, gene)

# fig.show()
