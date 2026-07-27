<!DOCTYPE html>
<html lang="de-de" dir="ltr">
<head>
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<meta http-equiv="X-UA-Compatible" content="IE=edge" />
	<meta charset="utf-8" />
	<meta name="generator" content="Joomla! - Open Source Content Management" />
	<title>glaszabosnu.ch - Administration</title>
	<link href="/administrator/templates/isis/favicon.ico" rel="shortcut icon" type="image/vnd.microsoft.icon" />
	<link href="/media/jui/css/chosen.css?6406ee0828429ac55f5af084c3cc970e" rel="stylesheet" />
	<link href="/administrator/templates/isis/css/template.css?6406ee0828429ac55f5af084c3cc970e" rel="stylesheet" />
	<style>

	@media (max-width: 480px) {
		.view-login .container {
			margin-top: -170px;
		}
		.btn {
			font-size: 13px;
			padding: 4px 10px 4px;
		}
	}
	</style>
	<script type="application/json" class="joomla-script-options new">{"csrf.token":"d3186786f759ab5001ccaff88eb85f16","system.paths":{"root":"","base":"\/administrator"},"system.keepalive":{"interval":840000,"uri":"\/administrator\/index.php"}}</script>
	<script src="/media/system/js/core.js?6406ee0828429ac55f5af084c3cc970e"></script>
	<!--[if lt IE 9]><script src="/media/system/js/polyfill.event.js?6406ee0828429ac55f5af084c3cc970e"></script><![endif]-->
	<script src="/media/system/js/keepalive.js?6406ee0828429ac55f5af084c3cc970e"></script>
	<script src="/media/jui/js/jquery.min.js?6406ee0828429ac55f5af084c3cc970e"></script>
	<script src="/media/jui/js/jquery-noconflict.js?6406ee0828429ac55f5af084c3cc970e"></script>
	<script src="/media/jui/js/jquery-migrate.min.js?6406ee0828429ac55f5af084c3cc970e"></script>
	<script src="/media/jui/js/bootstrap.min.js?6406ee0828429ac55f5af084c3cc970e"></script>
	<script src="/media/jui/js/chosen.jquery.min.js?6406ee0828429ac55f5af084c3cc970e"></script>
	<!--[if lt IE 9]><script src="/media/jui/js/html5.js?6406ee0828429ac55f5af084c3cc970e"></script><![endif]-->
	<script>
jQuery(function($){ initTooltips(); $("body").on("subform-row-add", initTooltips); function initTooltips (event, container) { container = container || document;$(container).find(".hasTooltip").tooltip({"html": true,"container": "body"});} });
	jQuery(function ($) {
		initChosen();
		$("body").on("subform-row-add", initChosen);

		function initChosen(event, container)
		{
			container = container || document;
			$(container).find(".advancedSelect").chosen({"disable_search_threshold":10,"search_contains":true,"allow_single_deselect":true,"placeholder_text_multiple":"Werte eingeben oder ausw\u00e4hlen","placeholder_text_single":"Wert ausw\u00e4hlen","no_results_text":"Keine passenden Ergebnisse gefunden!"});
		}
	});
	
	</script>

</head>
<body class="site com_login view-login layout-default task- itemid- ">
	<!-- Container -->
	<div class="container">
		<div id="content">
			<!-- Begin Content -->
			<div id="element-box" class="login well">
									<img src="/administrator/templates/isis/images/joomla.png" alt="glaszabosnu.ch" />
								<hr />
				<div id="system-message-container">
	</div>

				<form action="/administrator/index.php" method="post" id="form-login" class="form-inline">
	<fieldset class="loginform">
		<div class="control-group">
			<div class="controls">
				<div class="input-prepend input-append">
					<span class="add-on">
						<span class="icon-user hasTooltip" title="Benutzername"></span>
						<label for="mod-login-username" class="element-invisible">
							Benutzername						</label>
					</span>
					<input name="username" tabindex="1" id="mod-login-username" type="text" class="input-medium" placeholder="Benutzername" size="15" autofocus="true" />
					<a href="https://www.glaszabosnu.ch/index.php?option=com_users&view=remind" class="btn width-auto hasTooltip" title="Benutzername vergessen?">
						<span class="icon-help"></span>
					</a>
				</div>
			</div>
		</div>
		<div class="control-group">
			<div class="controls">
				<div class="input-prepend input-append">
					<span class="add-on">
						<span class="icon-lock hasTooltip" title="Passwort"></span>
						<label for="mod-login-password" class="element-invisible">
							Passwort						</label>
					</span>
					<input name="passwd" tabindex="2" id="mod-login-password" type="password" class="input-medium" placeholder="Passwort" size="15"/>
					<a href="https://www.glaszabosnu.ch/index.php?option=com_users&view=reset" class="btn width-auto hasTooltip" title="Passwort vergessen?">
						<span class="icon-help"></span>
					</a>
				</div>
			</div>
		</div>
							<div class="control-group">
				<div class="controls">
					<div class="input-prepend">
						<span class="add-on">
							<span class="icon-comment hasTooltip" title="Sprache"></span>
							<label for="lang" class="element-invisible">
								Sprache							</label>
						</span>
						<select id="lang" name="lang" class="advancedSelect" tabindex="4">
	<option value="" selected="selected">Sprache - Standard</option>
	<option value="bs-BA">Bosanski (Bosnia and Herzegovina)</option>
	<option value="de-CH">Deutsch (Schweiz)</option>
	<option value="de-DE">Deutsch (Deutschland)</option>
	<option value="en-GB">English (United Kingdom)</option>
</select>
					</div>
				</div>
			</div>
				<div class="control-group">
			<div class="controls">
				<div class="btn-group">
					<button tabindex="5" class="btn btn-primary btn-block btn-large login-button">
						<span class="icon-lock icon-white"></span> Anmelden					</button>
				</div>
			</div>
		</div>
		<input type="hidden" name="option" value="com_login"/>
		<input type="hidden" name="task" value="login"/>
		<input type="hidden" name="return" value="aW5kZXgucGhwP29wdGlvbj1jb21famNlJnRhc2s9cGx1Z2luLmRpc3BsYXkmcGx1Z2luPWltYWdlJjU3YWExOTVhOTYwM2U2ZDVmMDlkNmM2Yjk5OGRjNDE3PTEmY29udGV4dD0yMiZwcm9maWxlX2lkPTE="/>
		<input type="hidden" name="d3186786f759ab5001ccaff88eb85f16" value="1" />	</fieldset>
</form>

			</div>
			<noscript>
				Warnung! JavaScript muss für eine ordnungsgemäße Ausführung des Administrationsbereichs aktiviert sein.			</noscript>
			<!-- End Content -->
		</div>
	</div>
	<div class="navbar navbar-fixed-bottom hidden-phone">
		<p class="pull-right">
			&copy; 2026 glaszabosnu.ch		</p>
		<a class="login-joomla hasTooltip" href="https://www.joomla.org" target="_blank"  rel="noopener noreferrer" title="Joomla! ist freie, unter der GNU General Public License, veröffentlichte Software."><span class="icon-joomla"></span></a>
		<a href="http://www.glaszabosnu.ch/" target="_blank" class="pull-left">
			<span class="icon-out-2"></span>
			Zurück zur Website		</a>
	</div>
	
</body>
</html>
