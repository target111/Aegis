</head><body id="preview">
<h1><a id="Aegis_0"></a>Aegis</h1>
<p>Aegis is an irc based python botnet that features:</p>
<ul>
<li>An advanced SSH scanner that unlike others, really works.</li>
<li>DDOS  -  udp flooder</li>
<li>Execute commands on host</li>
</ul>
<p>You can also:</p>
<ul>
<li>easily implement new functions - very intuitive</li>
</ul>
<h3><a id="Compiling_10"></a>Compiling</h3>
<p>Aegis can be launched as a python script, but it is ultimately meant to be compiled as a win32 executable using pyinstaller.</p>
<p>First, install the dependencies:</p>
<ul>
<li>paramiko</li>
</ul>
<p>Then, configure <a href="http://aegis.py">aegis.py</a> according to your needs:</p>
<table class="table table-striped table-bordered">
<thead>
<tr>
<th>Variable</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr>
<td>irc_server</td>
<td>irc server to connect to</td>
</tr>
<tr>
<td>irc_port</td>
<td>the port on which the server is running</td>
</tr>
<tr>
<td>irc_channels</td>
<td>the channels the bot should join (space separated)</td>
</tr>
<tr>
<td>use_ssl</td>
<td>Use ssl to connect?</td>
</tr>
<tr>
<td>command_character</td>
<td>The bot will only respond when called with this prefix.</td>
</tr>
<tr>
<td>disabled</td>
<td>True/False disabled by default when joining.</td>
</tr>
</tbody>
</table>
<p>Finally compile to script into a single exe using pyinstaller (this has to be done on a windows machine):</p>
<pre><code class="language-sh">$ <span class="hljs-built_in">cd</span> Aegis
$ pyinstaller --onefile --noconsole aegis.py
</code></pre>
<p>That’s it! You have a fully standalone agent. (dist/aegis.exe)</p>

</body></html>
