use chrono::Utc;
use clap::Parser;
use serde::Serialize;
use sled::{Config, Db};
use std::path::PathBuf;
use uuid::Uuid;

#[derive(Parser)]
#[command(author, version, about = "Rust RBAC evaluator for Verdict")]
struct Args {
    role: String,
    action: String,
    resource: String,
    #[arg(long)]
    session_id: Option<String>,
}

#[derive(Serialize)]
struct Decision {
    allowed: bool,
    decision: String,
    reason: String,
    role: String,
    action: String,
    resource: String,
    timestamp: String,
    session_id: Option<String>,
}

struct Engine {
    db: Db,
}

impl Engine {
    fn open() -> Self {
        let path = PathBuf::from("rust_rbac_logs.db");
        let db = Config::default().path(path).flush_every_ms(Some(50)).open().unwrap();
        Self { db }
    }

    fn log(&self, decision: &Decision) {
        let log_tree = self.db.open_tree("logs").unwrap();
        let stats_tree = self.db.open_tree("stats").unwrap();
        let key = format!("{}-{}", decision.timestamp, Uuid::new_v4());
        log_tree
            .insert(key.as_bytes(), serde_json::to_vec(decision).unwrap())
            .unwrap();
        let stat_key = format!("stat:{}:{}:{}", decision.role, decision.action, decision.decision);
        stats_tree
            .update_and_fetch(stat_key.as_bytes(), |old| {
                let count = old
                    .and_then(|bytes| String::from_utf8(bytes.to_vec()).ok())
                    .and_then(|value| value.parse::<u64>().ok())
                    .unwrap_or(0)
                    + 1;
                Some(count.to_string().into_bytes())
            })
            .unwrap();
        self.db.flush().unwrap();
    }
}

fn normalize(value: &str) -> String {
    value.trim().to_lowercase()
}

fn compute_score(role: &str, action: &str, resource: &str) -> f64 {
    let role_score = match role {
        "admin" => 4.0,
        "viewer" => 1.6,
        _ => 0.8,
    };
    let action_score = match action {
        "read" => 1.0,
        "write" => 0.7,
        "delete" => -0.2,
        _ => -0.5,
    };
    let resource_risk: f64 = ["secret", "config", "admin"]
        .into_iter()
        .filter(|keyword| resource.contains(keyword))
        .map(|_| -0.4)
        .sum();
    let resource_signal: f64 = ["audit", "system", "user", "data", "settings"]
        .into_iter()
        .filter(|keyword| resource.contains(keyword))
        .map(|keyword| if keyword == &"audit" { 0.7 } else { 0.2 })
        .sum();
    let length_bonus = f64::min(resource.len() as f64 / 50.0, 0.5);
    role_score + action_score + resource_risk + resource_signal + length_bonus
}

fn build_decision(role: &str, action: &str, resource: &str, session_id: Option<String>) -> Decision {
    let normalized_role = normalize(role);
    let normalized_action = normalize(action);
    let normalized_resource = normalize(resource);
    let score = compute_score(&normalized_role, &normalized_action, &normalized_resource);
    let allowed = score >= 1.5;
    Decision {
        allowed,
        decision: if allowed { "allow".to_string() } else { "deny".to_string() },
        reason: format!(
            "score {:.2} computed from role={}, action={}, resource={}",
            score, normalized_role, normalized_action, normalized_resource
        ),
        role: normalized_role,
        action: normalized_action,
        resource: normalized_resource,
        timestamp: Utc::now().to_rfc3339_opts(chrono::SecondsFormat::Millis, true),
        session_id,
    }
}

fn main() {
    let args = Args::parse();
    let engine = Engine::open();
    let decision = build_decision(args.role.as_str(), args.action.as_str(), args.resource.as_str(), args.session_id);
    engine.log(&decision);
    println!("{}", serde_json::to_string(&decision).unwrap());
}
