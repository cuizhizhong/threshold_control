function layout_matlab
% 只读取保存结果并调整论文版式；不运行数值实验入口。
here = fileparts(mfilename('fullpath'));
root = fileparts(fileparts(here));
out = fullfile(fileparts(here), 'figures', 'layout_v5');
addpath(fullfile(root, 'scenario1_threshold_landscape', 'common'));
set_graphics_defaults();
set(groot, 'DefaultFigureVisible', 'off');
T = readtable(fullfile(root, 'archive_unused', 'generated_snapshots', ...
    'scenario1_threshold_landscape_current_run', 'output_csv', 'landscape_summary.csv'));
assert(height(T) == 28438);
style = scenario1_main_plot_style();
size2 = [451.28, 230];
fig = figure('Units','points','Position',[100 100 size2],'Color','w','Visible','off');
for panel = 1:2
    ax = axes(fig, 'Position', [0.095+(panel-1)*0.49, 0.17, 0.38, 0.75]);
    hold(ax,'on'); scenario1_main_plot_style(ax);
    if panel == 1
        values = [4 5 8 10 12]; rows = struct([]);
        for k=1:numel(values)
            row = T(abs(T.c0-values(k))<1e-10 & abs(T.eta_frac-.05)<1e-10,:);
            rows = append_row(rows,table_row_to_struct(row),k);
        end
    else
        values = [.002 .006 .010 .020]; rows = struct([]);
        for k=1:numel(values)
            row = T(abs(T.c0-10)<1e-10 & abs(T.eta_frac-values(k))<1e-10,:);
            rows = append_row(rows,table_row_to_struct(row),k);
        end
    end
    colors = style.blues(round(linspace(1,5,numel(rows))),:);
    xmax = max([rows.t2]+.08*[rows.Delta_t]);
    ymax = min(1,1.08*max([rows.q_max])+.02);
    h0 = plot(ax,[0 xmax],[rows(1).q0 rows(1).q0],'--','Color',style.gray,'LineWidth',style.reference_width);
    qi = 1-1/(2*(1-rows(1).beta));
    hi = plot(ax,[0 xmax],[qi qi],':','Color',style.q_inf,'LineWidth',1.2);
    hh = gobjects(numel(rows),1); labels = cell(numel(rows),1);
    for k=1:numel(rows)
        r = rows(k);
        tau = linspace(0,r.Delta_t,max(350,ceil(12*r.Delta_t)));
        hh(k)=plot(ax,r.t1+tau,q_control_tau(r,tau),'-','Color',colors(k,:),'LineWidth',style.line_width);
        plot(ax,r.t1,r.q_max,'^','Color',colors(k,:),'MarkerFaceColor','w','MarkerSize',style.marker_size,'LineWidth',style.reference_width,'HandleVisibility','off');
        plot(ax,r.t2,r.q0,'|','Color',colors(k,:),'MarkerSize',7,'LineWidth',1.2,'HandleVisibility','off');
        info=scenario1_inflection_point(r);
        if info.has_inflection
            plot(ax,info.t_inf,info.q_at_inf,'o','Color','w','MarkerFaceColor',style.accent,'MarkerSize',style.marker_size,'LineWidth',.7,'HandleVisibility','off');
        end
        if panel==1
            labels{k}=sprintf('$c_0=%g$',r.c0);
        else
            labels{k}=sprintf('$\\eta/N=%g\\%%$',r.eta_percent);
        end
    end
    xlabel(ax,'$t$','FontSize',9); ylabel(ax,'$q_c(t)$','FontSize',9);
    xlim(ax,[0 xmax]); ylim(ax,[0 ymax]);
    lgd=legend(ax,[hh;hi;h0],[labels;{'$q_{\rm inf}$';'$q_0$'}], ...
        'Location','northeast','Interpreter','latex','FontSize',7.5,'Box','off');
    if isprop(lgd,'ItemTokenSize'), lgd.ItemTokenSize=[12 8]; end
    panel_label(ax,panel);
end
export_final(fig,fullfile(out,'baseline_q_joint'),size2,here);
for kind=1:2
    sz=[451.28 88/25.4*72];
    fig=figure('Units','points','Position',[100 100 sz],'Color','w','Visible','off');
    fields={'t1','Delta_t','t_end','q_max','J','I_t_cum'};
    yl={'$t_1$','$\Delta t$','$t_{\rm end}$','$q_{\max}$','$J$','$I_{t_{\rm cum}}$'};
    colors=style.blues(round(linspace(1,5,4)),:);
    for k=1:6
        col=mod(k-1,3); row=floor((k-1)/3);
        ax=axes(fig,'Position',[.080+col*.322,.59-row*.46,.242,.315]);
        hold(ax,'on'); scenario1_main_plot_style(ax);
        hh=gobjects(4,1); labels=cell(4,1);
        for j=1:4
            if kind==1
                vals=[.002 .006 .010 .020];
                sub=T(abs(T.eta_frac-vals(j))<1e-10,:);
            else
                vals=[5 8 10 12];
                sub=T(abs(T.c0-vals(j))<1e-10,:);
            end
            sub=sub(logical(sub.valid)&isfinite(sub.(fields{k})),:);
            if kind==1
                x=sub.c0; labels{j}=sprintf('$\\eta/N=%g\\%%$',100*vals(j));
            else
                sub=sortrows(sub,'eta_percent'); x=sub.eta_percent;
                labels{j}=sprintf('$c_0=%g$',vals(j));
            end
            hh(j)=plot(ax,x,sub.(fields{k}),'-','Color',colors(j,:),'LineWidth',style.line_width,'Marker','none');
            if kind==1 && k==2
                [v,ix]=max(sub.Delta_t);
                plot(ax,sub.c0(ix),v,'o','Color','w','MarkerFaceColor',style.accent,'MarkerSize',style.marker_size,'LineWidth',.7,'HandleVisibility','off');
            end
        end
        if kind==1
            xlabel(ax,'$c_0$','FontSize',9); xlim(ax,[2.3 14]);
        else
            set(ax,'XScale','log'); xlabel(ax,'$\eta/N\;(\%)$','FontSize',9);
            xlim(ax,[.2 5]); xticks(ax,[.2 .5 1 2 5]); xticklabels(ax,{'0.2','0.5','1','2','5'});
            if k==4
                ylim(ax,[.45 .85]); yticks(ax,.45:.10:.85);
                yticklabels(ax,{'0.45','0.55','0.65','0.75','0.85'});
            end
        end
        ylabel(ax,yl{k},'FontSize',10.5);
        panel_label(ax,k);
        if k==3
            lgd=legend(ax,hh,labels,'Location','northeast','Interpreter','latex','FontSize',7.5,'Box','off');
            if isprop(lgd,'ItemTokenSize'), lgd.ItemTokenSize=[10 8]; end
            if kind==1
                ylim(ax,[0 350]);
                drawnow;
                lgd.Units='normalized'; lp=lgd.Position;
                lgd.Position=[.975-lp(3),.99-lp(4),lp(3),lp(4)];
            end
        end
    end
    names={'c0_sensitivity_selected_eta','eta_sensitivity_selected_c0'};
    export_final(fig,fullfile(out,names{kind}),sz,here);
end
fprintf('MATLAB_LAYOUT_V5_OK\n');
end

function panel_label(ax,k)
text(ax,-.02,1.015,sprintf('(%c)','a'+k-1),'Units','normalized', ...
    'FontName','Times New Roman','FontSize',11,'FontWeight','bold', ...
    'Interpreter','none','Color',[.133 .133 .133], ...
    'HorizontalAlignment','left','VerticalAlignment','bottom','Clipping','off');
end

function export_final(fig,stem,sz,here)
drawnow;
aa=findall(fig,'Type','axes'); positions=zeros(numel(aa),4);
series=cell(numel(aa),1);
for k=1:numel(aa)
    aa(k).Units='points'; positions(k,:)=aa(k).Position;
    ll=findall(aa(k),'Type','line'); records=cell(numel(ll),1);
    for j=1:numel(ll)
        records{j}=struct('x',ll(j).XData,'y',ll(j).YData,'color',ll(j).Color,'width',ll(j).LineWidth,'style',ll(j).LineStyle,'marker',ll(j).Marker);
    end
    series{k}=records;
end
% 轴矩形由 MATLAB 测量，供独立核查；不以外边框代替绘图区。
[~,name]=fileparts(stem);
f=fopen(fullfile(here,'qa',[name '.matlab_geometry.json']),'w');
fprintf(f,'%s',jsonencode(struct('size_bp',sz,'positions',positions,'series',{series}))); fclose(f);
assert(save_figure_safe(fig,[stem '.pdf'],[],sz),'PDF export failed');
print(fig,[stem '.png'],'-dpng','-r300');
print(fig,[stem '.svg'],'-dsvg','-painters');
close(fig);
end
