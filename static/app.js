let analytics = null;
let monthlyChart = null;
let categoryChart = null;
const currency = value => new Intl.NumberFormat("en-IN",{style:"currency",currency:"INR",maximumFractionDigits:2}).format(value || 0);
const categoryColors = ["#19a879","#8974e8","#5b8def","#e9a04b","#e47791","#4cb6c2","#9aa7b8"];
const byId = id => document.getElementById(id);

async function loadDashboard(){
  const response = await fetch("/api/analytics");
  analytics = await response.json();
  byId("month-total").textContent = currency(analytics.month_total);
  byId("all-total").textContent = currency(analytics.total);
  byId("transaction-count").textContent = analytics.transaction_count;
  byId("average-spend").textContent = currency(analytics.average);
  const change = analytics.month_change_percent;
  byId("month-change").textContent = change === null ? "No previous-month comparison" :
    (change > 0 ? "↑ " : change < 0 ? "↓ " : "") + Math.abs(change) + "% vs last month";
  renderCharts(); renderTransactions();
}
function renderCharts(){
  const months = Object.keys(analytics.monthly_totals || {});
  byId("monthly-empty").style.display = months.length ? "none" : "flex";
  if(monthlyChart) monthlyChart.destroy();
  monthlyChart = new Chart(byId("monthly-chart"),{type:"line",data:{labels:months.map(m=>new Date(m+"-02").toLocaleDateString("en-IN",{month:"short",year:"2-digit"})),datasets:[{data:Object.values(analytics.monthly_totals),borderColor:"#19a879",backgroundColor:"rgba(25,168,121,.10)",fill:true,tension:.38,pointRadius:3,pointBackgroundColor:"#19a879",borderWidth:2}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false},tooltip:{callbacks:{label:c=>currency(c.raw)}}},scales:{x:{grid:{display:false},ticks:{color:"#9aa5b4",font:{size:10}}},y:{beginAtZero:true,grid:{color:"#f0f2f6"},ticks:{color:"#9aa5b4",font:{size:10},callback:v=>"₹"+v}}}}});
  const entries = Object.entries(analytics.category_totals || {}).sort((a,b)=>b[1]-a[1]);
  byId("category-empty").style.display = entries.length ? "none" : "flex";
  if(categoryChart) categoryChart.destroy();
  categoryChart = new Chart(byId("category-chart"),{type:"doughnut",data:{labels:entries.map(x=>x[0]),datasets:[{data:entries.map(x=>x[1]),backgroundColor:categoryColors,borderWidth:0,hoverOffset:5}]},options:{cutout:"72%",responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false},tooltip:{callbacks:{label:c=>c.label+": "+currency(c.raw)}}}}});
  byId("category-legend").innerHTML = entries.map(([name,total],i)=>'<div class="legend-item"><span class="legend-dot" style="background:'+categoryColors[i%categoryColors.length]+'"></span><span>'+escapeHtml(name.charAt(0).toUpperCase()+name.slice(1))+'</span><strong>'+currency(total)+'</strong></div>').join("");
}
function escapeHtml(value){return String(value).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));}
function renderTransactions(){
  const search = (byId("transaction-search").value || "").toLowerCase();
  const category = byId("category-filter").value;
  const items = (analytics.expenses || []).filter(e=>(!category||e.category===category)&&(!search||(e.description+" "+e.category+" "+e.date).toLowerCase().includes(search)));
  const shown = byId("show-all").dataset.all === "true" ? items : items.slice(0,8);
  byId("transactions-body").innerHTML = shown.length ? shown.map(e=>'<tr><td>'+escapeHtml(e.description)+'</td><td><span class="category-pill">'+escapeHtml(e.category)+'</span></td><td>'+e.date+'</td><td class="amount-cell">'+currency(e.amount)+'</td><td><div class="row-actions"><button class="icon-button" data-edit="'+e.id+'">Edit</button><button class="icon-button" data-delete="'+e.id+'">Delete</button></div></td></tr>').join("") : '<tr><td colspan="5" class="table-empty">No matching transactions found.</td></tr>';
}
byId("transaction-search").addEventListener("input",renderTransactions);
byId("category-filter").addEventListener("change",renderTransactions);
byId("show-all").addEventListener("click",()=>{const b=byId("show-all");b.dataset.all=b.dataset.all==="true"?"false":"true";b.textContent=b.dataset.all==="true"?"Show less ↑":"Show all ↗";renderTransactions();});
byId("transactions-body").addEventListener("click",async e=>{
  const edit=e.target.dataset.edit, del=e.target.dataset.delete;
  if(edit!==undefined){const item=analytics.expenses.find(x=>x.id===Number(edit));if(!item)return;byId("edit-id").value=item.id;byId("edit-amount").value=item.amount;byId("edit-category").value=item.category;byId("edit-description").value=item.description;byId("edit-date").value=item.date;byId("edit-dialog").showModal();}
  if(del!==undefined&&confirm("Delete this expense?")){const r=await fetch("/delete/"+del,{method:"POST"});if(r.ok)loadDashboard();else alert(await r.text());}
});
function closeEdit(){byId("edit-dialog").close();}
byId("close-dialog").addEventListener("click",closeEdit);byId("cancel-edit").addEventListener("click",closeEdit);
byId("edit-form").addEventListener("submit",async e=>{e.preventDefault();const id=byId("edit-id").value;const data=new URLSearchParams({amount:byId("edit-amount").value,category:byId("edit-category").value,description:byId("edit-description").value,date:byId("edit-date").value});const r=await fetch("/edit/"+id,{method:"POST",headers:{"Content-Type":"application/x-www-form-urlencoded"},body:data});if(r.ok){closeEdit();loadDashboard();}else alert(await r.text());});
byId("expense-form").addEventListener("submit",async e=>{e.preventDefault();const form=e.currentTarget;const r=await fetch("/add",{method:"POST",body:new FormData(form)});const message=byId("form-message");if(r.ok){form.reset();byId("date").value=new Date().toISOString().slice(0,10);message.style.color="#15966e";message.textContent="Expense added successfully.";loadDashboard();}else{message.textContent=await r.text();}});
function addMessage(text,who){const node=document.createElement("div");node.className="chat-bubble "+(who==="user"?"user-bubble":"assistant-bubble");node.textContent=text;byId("chat-messages").appendChild(node);byId("chat-messages").scrollTop=byId("chat-messages").scrollHeight;return node;}
async function askAssistant(message){addMessage(message,"user");const wait=addMessage("Thinking through your spending...","assistant");byId("chat-input").disabled=true;byId("chat-form").querySelector("button").disabled=true;try{const r=await fetch("/api/assistant",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({message})});const data=await r.json();wait.textContent=data.answer||"I couldn't prepare an answer."; }catch(err){wait.textContent="Something went wrong. Please try again.";}finally{byId("chat-input").disabled=false;byId("chat-form").querySelector("button").disabled=false;byId("chat-input").focus();}}
byId("chat-form").addEventListener("submit",e=>{e.preventDefault();const input=byId("chat-input");const message=input.value.trim();if(message){input.value="";askAssistant(message);}});
document.querySelectorAll("[data-prompt]").forEach(button=>button.addEventListener("click",()=>askAssistant(button.dataset.prompt)));
byId("date").value=new Date().toISOString().slice(0,10);
loadDashboard().catch(()=>{byId("transactions-body").innerHTML='<tr><td colspan="5" class="table-empty">Could not load your expenses.</td></tr>';});
