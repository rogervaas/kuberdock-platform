<div class="breadcrumbs-wrapper">
    <div class="container breadcrumbs" id="breadcrumbs">
        <ul class="breadcrumb">
            <li class="active">Nodes</li>
        </ul>
        <div class="control-group">
            <button id="add_node">Add Node</button>
            <div class="nav-search" id="nav-search"></div>
            <input type="text" placeholder="Search" class="nav-search-input" id="nav-search-input" autocomplete="off">
        </div>
    </div>
</div>
<div class="container">
    <table id="nodelist-table" class="table">
        <thead>
            <tr>
                <th class="hostname">Node<b class="caret <%= sortingType.hostname == -1 ? 'rotate' : '' %>"></b></th>
                <th class="ip">IP<b class="caret <%= sortingType.ip == -1 ? 'rotate' : '' %>"></b></th>
                <th class="kube_type">Kube Type<b class="caret <%= sortingType.kube_type == -1 ? 'rotate' : '' %>"></b></th>
                <!-- <th class="hostname">Kube capacity<b class="caret"></b><br>(used/max)</th> -->
                <!-- <th>Average<b class="caret"></b><br>CPU usage</th> -->
                <!-- <th>Active pods<b class="caret"></b><br>(containers)</th> -->
                <th class="status">Status<b class="caret <%= sortingType.status == -1 ? 'rotate' : '' %>"></b></th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody></tbody>
    </table>
</div>
